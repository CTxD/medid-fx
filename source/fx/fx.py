import uuid
import joblib
import os
import logging
import pickle
import copy
import base64

from flask import jsonify
from .colorx import cx
from .utils import encoding2tmpfile, promedimgsplit, showimg
from ..repository import firestore
from source.repository.firestore import FBManager
from source.fx import shapex
from source.models.v1.PillFeatureSchema import PillFeature


logger = logging.getLogger(__name__)


class MatchResult():
    pillfeature: PillFeature

    def __init__(self, prob, pf, imgstring='', substance=''):
        self.probability = prob
        self.pillfeature = pf
        self.imgstring = imgstring
        self.substance = substance

    def serialize(self):
        try:
            return {
                'probability': self.probability,
                'imgstring': self.imgstring.decode('UTF-8'),
                'name': self.pillfeature['name'],
                'side': self.pillfeature['side'],
                'substance': self.substance,
                'kind': self.pillfeature['kind'],
                'strength': self.pillfeature['strength'],
            }
        except Exception:
            print(self.pillfeature['name'])
            print(self.imgstring)


def getmatches(pillrepresentation):
    fb = FBManager()

    s = shapex.ShapePreprocessor()
    sd = shapex.ShapeDescriptor()
    #img = s.load_image_from_bytestring_and_dims(pillrepresentation['imgstring'], pillrepresentation['height'], pillrepresentation['width'])
    img = s.load_image_from_bytestring(pillrepresentation['imgstring'])
    path = 'resources/p00.jpg'
    img = s.load_image_from_file(path)

    huimg = s.grayscale_and_brightness(copy.copy(img))
    hu, conts = sd.test_calc_hu_moments_from_single_img(huimg)

    model = fb.get_latest_model()
    svmmodel = model['svmmodel']

    pillfeatures = model['pillfeatures']

    results = list(filter(lambda p: pillrepresentation['imprintid'] in p['imprint'] or (
        pillrepresentation['imprintid'] == 'Tekst eller tal' and ('/resource/media/' not in p['imprint'] and 'Intet præg' not in p['imprint'])), pillfeatures))
    results = list(filter(lambda p: len(p['shapefeature']) == 7, results))

    labels = cx.getcx(path, conts, svmmodel)
    results = list(filter(lambda p: labels[0] in p['colorfeature'], results))

    def getPackedPill(p): return (fb.get_specific_pill(p['name']))

    def getEncoding(p, pacp): return (next(
        x for x in pacp['photofeatures'] if x['strength'] == p['strength']))['imageEncoding'][0]

    mrs = list(map(lambda p: MatchResult(
        abs(sd.calc_cosine_similarity(hu, p['shapefeature'])), p), results))
    sortedMrs = sorted(mrs, key=lambda m: m.probability, reverse=False)[:10]
    

    for mr in sortedMrs:
        packed = getPackedPill(mr.pillfeature)
        if packed is None:
            sortedMrs.remove(mr)
            continue
            

        mr.imgstring = getEncoding(mr.pillfeature, packed)
        if mr.imgstring is '':    
            sortedMrs.remove(mr)
            continue
        mr.substance = packed['substance']


    json = jsonify([r.serialize() for r in sortedMrs])
    return json


def train():
    # Make FBM instance
    fbm = firestore.FBManager()

    # Get list of all pills, convert the image encoding to an image, then crop image, save each
    # sides encoding and make a copy of the pillobj with each image encoding
    logger.info(
        'Training model started. Fetching and filtering all pills (slim)')
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

    logger.info(f'All pills: {len(allpills)}; filtered: {len(filteredpills)}')

    # Train the color SVM
    logger.info('Traning color SVM on filtered pills')
    svmmodelcontent = pickle.dumps(cx.train(filteredpills))

    sd = shapex.ShapeDescriptor()
    sp = shapex.ShapePreprocessor()
    pillfeatures = []
    failed = []
    logger.info(
        f'Calculating pillfeature for all pills ({len(filteredpills)} pills)')
    for pillobj in filteredpills:
        with encoding2tmpfile.Encoding2TmpFile(pillobj['image'][0]) as imgpath:
            try:
                cf = cx.compreslabels(pillobj['color'])
                sf = sd.calc_hu_moments_from_single_img(
                    sp.load_image_from_file(imgpath))

                pillfeatures.append(
                    PillFeature(
                        name=pillobj['name'],
                        side=pillobj['side'],
                        kind=pillobj['kind'],
                        strength=pillobj['strength'],
                        imprint=pillobj['imprint'],
                        colorfeature=cf,
                        shapefeature=sf
                    ).__dict__
                )
            except Exception:
                failed.append(
                    f'{pillobj["name"]}, {pillobj["kind"]} {pillobj["strength"]}')

    logger.info(f'Finished calculating pillfeatures for {len(pillfeatures)} pills ({len(failed)} failed)')  # noqa

    # Upload model + SVM model
    model = {
        'pillfeatures': pillfeatures,
        'svmmodel': svmmodelcontent
    }

    # Upload model
    fbm.add_model(model)

    logging.info('Training finished. Model has been uploaded.')

    if failed:
        print('The following pills failed:')
        import json
        print(json.dumps(failed, indent=4))
        print(len(failed))
