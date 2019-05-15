from .colorx import cx
from .utils import encoding2img, promedimgsplit
from ..repository import firestore


def getmatches(imageencoding):
    with encoding2img.Encoding2IMG(imageencoding) as imgpath:
        cxfeature = cx.getcx(imgpath)


def train():
    # Make FBM instance
    fbm = firestore.FBManager()

    # Get list of all pills, convert the image encoding to an image, then crop image, save each
    # sides encoding and make a copy of the pillobj with each image encoding
    allpills = []
    for pillobj in fbm.get_all_pills_slim():
        if not pillobj['image'] or isinstance(pillobj['image'][0], dict):
            continue

        pillobj['image'][0] = bytes(pillobj['image'][0], encoding='utf-8')
        allpills.extend(promedimgsplit.promedimgsplit(pillobj))

    # Train model
    # for pillobj in allpills:
    # Get shape vector
    # Get color vector
    # combine

    # Add to matrix

    # Upload model + SVM model


# def parse(obj):
#     if isinstance(obj, dict):
#         return dicttype(obj)
#     elif isinstance(obj, list):
#         return listtype(obj)
#     elif isinstance(obj, str):
#         return obj
#     elif isinstance(obj, bytes):
#         return obj.decode('utf-8')
#     else:
#         print('Unknown parse: (Type:', type(obj), ')', obj)
#         return obj


# def dicttype(value):
#     result = {}
#     for k, v in value.items():
#         result[k] = parse(v)

#     return result


# def listtype(value):
#     result = []
#     for elem in value:
#         result.append(parse(elem))

#     return result


# def savetofile():
#     import json
#     allpills = fbm.get_all_pills_slim()
#     with open('resources/allpills2.json', mode='w+') as f:
#         allpillslist = []
#         for pillobj in allpills:
#             pill = {}
#             for k, v in pillobj.items():
#                 pill[k] = parse(v)

#             allpillslist.append(pill)

#         json.dump(allpillslist, f, indent=4, ensure_ascii=False)
#         json.dump(allpills, f, indent=4)
