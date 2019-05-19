import logging
import uuid
import time
import os
import json
from typing import Dict, List

from firebase_admin import credentials, firestore, initialize_app
from google.cloud.firestore import Client
from ..models.v1 import MatchSchema, ExtendedSchema, SlimSchema, MetaSchema, ErrorSchema, PillFeatureSchema  # type: ignore # noqa

from source.config import CONFIG


logger = logging.getLogger(__name__)


class FBManager:
    def __init__(self):
        certificate = credentials.Certificate(
            os.path.join(os.getcwd(), CONFIG["CERT"])
        )
        self.db: Client = firestore.client(initialize_app(certificate, name=str(uuid.uuid4())))

    def _convert_obj_to_dict(self, obj):
        class_dict = {}

        def parsekeyvalue(key, value):
            if key.startswith('__'):
                return None
            if callable(value):
                return None
            if isinstance(value, list):
                newattrvalue = []
                for oldvalue in value:
                    if isinstance(oldvalue, (str, int, float, bool, bytes)):
                        newattrvalue.append(oldvalue)
                    else:
                        newattrvalue.append(self._convert_obj_to_dict(oldvalue))
                value = newattrvalue
            return value
        
        for attr in dir(obj):
            value = parsekeyvalue(attr, getattr(obj, attr))
            if value is None:
                continue
            class_dict[attr] = value
        return class_dict

    def get_specific_pill(self, document_id: str):
        print(self.db.collection("pills").document(document_id).get().to_dict())
        return self.db.collection("pills").document(document_id).get().to_dict()

    def get_all_pills_slim(self):
        if CONFIG['USELOCAL']:
            return json.load(open('resources/allpillsslim.json'))

        pills = []
        unpacked_pills = self.get_all_extended_pills()

        for item in unpacked_pills:
            for photo in item["photofeatures"]:
                slim_pill_schema = SlimSchema()
                slim_pill_schema.name = item["pillname"]
                slim_pill_schema.substance = item["substance"]
                slim_pill_schema.kind = photo["kind"]
                slim_pill_schema.strength = photo["strength"]
                slim_pill_schema.imprint = photo["imprint"]
                slim_pill_schema.score = photo["score"]
                slim_pill_schema.color = photo["colour"]
                slim_pill_schema.size = photo["sizeDimensions"]
                slim_pill_schema.image = photo["imageEncoding"]
                pills.append(slim_pill_schema.__dict__)
        return pills

    def get_all_extended_pills(self):
        pills = []
        res = self.db.collection("pills").get()

        for pill in res:
            pills.append(pill.to_dict())

        return pills

    def get_latest_model(self):
        if CONFIG['USELOCAL']:
            alldata = json.load(open('resources/model.json'))
            return {
                'svmmodel': bytes(alldata['svmmodel'], encoding='latin1'),
                'pillfeatures': alldata['pillfeatures']
            }

        svmmodelsnapshot = list(self.db.collection("svmmodel").get())[0]
        timestamp = svmmodelsnapshot.id
        
        allpfssnapshot = list(self.db.collection('pillfeatures').get())
        pfsbytimestamp = list(
            map(
                lambda x: x.to_dict(),
                filter(
                    lambda x: x.id.startswith(str(timestamp)),
                    allpfssnapshot
                )
            )
        )

        return {
            'pillfeatures': [pfs for pf in pfsbytimestamp for pfs in pf['pillfeatures']],
            'svmmodel': svmmodelsnapshot.to_dict()['svmmodel']
        }

    def add_model(self, model: Dict):
        timestamp = str(int(time.time()))

        pfsbyletter: Dict[str, List] = {}
        for pf in model['pillfeatures']:
            letter = pf['name'][0].lower()
            if letter not in pfsbyletter:
                pfsbyletter[letter] = []

            pfsbyletter[letter].append(pf)
        
        for letter, pfs in pfsbyletter.items():
            self.db.collection("pillfeatures").document(f'{timestamp}_{letter}').set(
                {
                    'pillfeatures': pfs
                }
            ) 

        self.db.collection("svmmodel").document(timestamp).set({'svmmodel': model['svmmodel']})