import os
import logging
import uuid

from firebase_admin import credentials, firestore, initialize_app
from google.cloud.firestore import Client
from ..models.v1 import MatchSchema, ExtendedSchema, SlimSchema, MetaSchema, ErrorSchema  # type: ignore # noqa

from source.config import CONFIG


logger = logging.getLogger(__name__)


class FBManager:
    def __init__(self):
        certificate = credentials.Certificate(
            os.path.join(os.getcwd(), CONFIG["CERT"])
        )
        self.db: Client = firestore.client(initialize_app(certificate, name=str(uuid.uuid4())))

    def get_specific_pill(self, document_id: str):
        print(self.db.collection("pills").document(document_id).get().to_dict())
        return self.db.collection("pills").document(document_id).get().to_dict()

    def get_all_pills_slim(self):
        pills = []
        unpacked_pills = self.get_all_extended_pills()

        for item in unpacked_pills:
            slim_pill_schema = SlimSchema()
            for photo in item["photofeatures"]:
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
