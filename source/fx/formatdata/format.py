from source.repository.firestore import FBManager
from source.fx import shapex


def hasimage(pill):
    return pill["image"] is not None and pill["image"] and not isinstance(pill['image'][0], dict)  


def getrelevantpills():
    fb = FBManager()
    allpils = fb.get_all_pills_slim()
    return filter(hasimage, allpils)


def makeschema():
    pills = getrelevantpills()
    s = shapex.ShapePreprocessor()
    for pill in pills:
        img = s.load_image_from_bytestring(pill["image"][0].decode("utf-8"))