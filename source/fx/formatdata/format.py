from source.repository.firestore import FBManager
from source.fx import shapex


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
        img = s.load_image_from_bytestring(pill["image"][0].decode("utf-8"))
        hm1, hm2 = sd.calc_hu_moments_from_img(img)
        if hm1 is None or hm2 is None:
                print(pill)
        #fb.add_or_update()
