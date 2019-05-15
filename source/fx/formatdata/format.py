from source.repository.firestore import FBManager
from source.fx import shapex
from source.models.v1.PillFeatureSchema import PillFeature



def hasimage(pill):
    return pill["image"] is not None and pill["image"] and not isinstance(pill['image'][0], dict)  


def getrelevantpills():
    fb = FBManager()
    allpils = fb.get_all_pills_slim()
    return filter(hasimage, allpils)


def buildmodel():
    pills = getrelevantpills()
    fb = FBManager()
    s = shapex.ShapePreprocessor()
    sd = shapex.ShapeDescriptor()
    for pill in pills:
        imgbs = bytes(pill['image'][0], encoding='utf-8')
        img = s.load_image_from_bytestring(imgbs)
        hm1, hm2 = sd.calc_hu_moments_from_img(img)
        right = PillFeature(pill['name'], pill['substance'], hm1, 'colour')
        left = PillFeature(pill['name'], pill['substance'], hm2, 'colour')
