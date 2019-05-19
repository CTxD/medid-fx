import uuid
import joblib 
import os
import logging
import pickle

from .colorx import cx
from .utils import encoding2tmpfile, promedimgsplit
from ..repository import firestore
from source.repository.firestore import FBManager
from source.fx import shapex
from source.models.v1.PillFeatureSchema import PillFeature


logger = logging.getLogger(__name__)


def getmatches(pillrepresentation):
    fb = FBManager()

    s = shapex.ShapePreprocessor()
    sd = shapex.ShapeDescriptor()
    img = s.load_image_from_bytestring(pillrepresentation['imgstring'])
    hu = sd.ShapeDescriptor(img)

    model = fb.get_latest_model()
    svmmodel = model['svmmodel']
    with encoding2tmpfile.Encoding2TmpFile(pillrepresentation['imgstring']) as tmpfile:
        labels = cx.getcx(tmpfile, svmmodel)

    pillfeatures = model['pillfeatures']
    # With pillfeatures, do the following (in any order):
        # Calculate hu-moments distance
        # Filter based on labels
        # Filter based on imprint


def train():
    # Make FBM instance
    fbm = firestore.FBManager()

    # Get list of all pills, convert the image encoding to an image, then crop image, save each
    # sides encoding and make a copy of the pillobj with each image encoding
    logger.info('Fetching and filtering all pills (slim)')
    allpills = []
    for pillobj in fbm.get_all_pills_slim():
        if not pillobj['image'] or isinstance(pillobj['image'][0], dict):
            continue

        pillobj['image'][0] = bytes(pillobj['image'][0], encoding='utf-8')
        allpills.extend(promedimgsplit.promedimgsplit(pillobj))

    # For now, we can not handle multi-colored pills, so we filter those out. Additionally, there 
    # exists color classifications, which are not actual colors, and these are also filtered out
    ignorecolors = ['Spættet', 'Gennemsigtig', 'Transparent']
    filteredpills = list(filter(
        lambda x: len(x['color']) == 1 and x['color'][0] not in ignorecolors,
        allpills
    ))

    # Train the color SVM
    logger.info('Traning color SVM on filtered pills')
    svmmodelcontent = pickle.dumps(cx.train(filteredpills))

    sd = shapex.ShapeDescriptor()
    sp = shapex.ShapePreprocessor()
    pillfeatures = []
    failed = []
    logger.info(f'Calculating pillfeature for all pills ({len(filteredpills)} pills)')
    for pillobj in filteredpills:
        with encoding2tmpfile.Encoding2TmpFile(pillobj['image'][0]) as imgpath:
            try:
                cf = cx.compreslabels(pillobj['color'])
                sf = sd.calc_hu_moments_from_single_img(sp.load_image_from_file(imgpath))
                
                pillfeatures.append(
                    PillFeature(
                        name=pillobj['name'],
                        side=pillobj['side'],
                        kind=pillobj['kind'],
                        strength=pillobj['strength'],
                        colorfeature=cf,
                        shapefeature=sf
                    ).__dict__
                )
            except Exception:
                failed.append(f'{pillobj["name"]}, {pillobj["kind"]} {pillobj["strength"]})
                continue

    logger.info(f'Finished calculating pillfeatures for {len(pillfeatures)} pills ({len(failed)} failed)') # noqa

    # Upload model + SVM model
    model = {
        'pillfeatures': pillfeatures,
        'svmmodel': svmmodelcontent# open(svmtmppath).read()
    }

    # Upload model
    fbm.add_model(model)

    logging.info('Training finished. Model has been uploaded.')

    if failed:
        print('The following pills failed:')
        print(failed)

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