from source.repository.firestore import FBManager
from source.fx import shapex
from source.models.v1.PillFeatureSchema import PillFeature

def getmatches(pillrepresentation):
    fb = FBManager()
    s = shapex.ShapePreprocessor()
    sd = shapex.ShapeDescriptor()
    img = s.load_image_from_bytestring(pillrepresentation['imgstring'])
    hu = sd.ShapeDescriptor(img)