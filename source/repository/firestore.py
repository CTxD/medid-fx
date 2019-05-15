import os
import logging
# from source.models.v1 import FeatureVectorSchema
from firebase_admin import credentials, firestore, initialize_app
from source.models.v1 import MatchSchema, ExtendedSchema, SlimSchema, MetaSchema, ErrorSchema, PillFeatureSchema  # type: ignore # noqa
import uuid
from google.cloud.firestore import Client


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
        # RETURN ALL PILLS FROM FILE
        import json
        return json.load(open('resources/allpillsslim.json'))
        
    # def get_all_pills_slim(self):
        
    #     pills = []
    #     unpacked_pills = self.get_all_extended_pills()

    #     for item in unpacked_pills:

    #         for photo in item["photofeatures"]:
                    # slim_pill_schema = SlimSchema()
    #             slim_pill_schema.name = item["pillname"]
    #             slim_pill_schema.substance = item["substance"]
    #             slim_pill_schema.kind = photo["kind"]
    #             slim_pill_schema.strength = photo["strength"]
    #             slim_pill_schema.imprint = photo["imprint"]
    #             slim_pill_schema.score = photo["score"]
    #             slim_pill_schema.color = photo["colour"]
    #             slim_pill_schema.size = photo["sizeDimensions"]
    #             slim_pill_schema.image = photo["imageEncoding"]
    #             pills.append(slim_pill_schema.__dict__)
    #     return pills

    def get_all_extended_pills(self):
        pills = []
        res = self.db.collection("pills").get()

        for pill in res:
            pills.append(pill.to_dict())

        return pills

    def add_pill_feature(self, collection_id: str, pill_feature: PillFeatureSchema): 
        temp = self._convert_obj_to_dict(pill_feature)
        self.db.collection(collection_id).document(pill_feature.pillname).set(temp) 