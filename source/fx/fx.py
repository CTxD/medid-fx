import uuid
import joblib 
import os
import logging
import pickle
import copy
import base64

from .colorx import cx
from .utils import encoding2tmpfile, promedimgsplit, showimg
from ..repository import firestore
from source.repository.firestore import FBManager
from source.fx import shapex
from source.models.v1.PillFeatureSchema import PillFeature


logger = logging.getLogger(__name__)


class MatchResult():
    pillfeature: PillFeature
    def __init__(self, prob, pf):
        self.probability = prob
        self.pillfeature = pf
    


def getmatches(pillrepresentation):
    fb = FBManager()

    s = shapex.ShapePreprocessor()
    sd = shapex.ShapeDescriptor()
    img = s.load_image_from_bytestring_and_dims(pillrepresentation['imgstring'], pillrepresentation['height'], pillrepresentation['width'])
    #img = s.load_image_from_bytestring(pillrepresentation['imgstring'])
    
    huimg = s.grayscale_and_brightness(img)
    hu = sd.test_calc_hu_moments_from_single_img(huimg)
    showimg.showimgs(['img'],[img])
    
    model = fb.get_latest_model()
    svmmodel = model['svmmodel']

    pillfeatures = model['pillfeatures']

    print(hu)


    results = list(filter(lambda p: pillrepresentation['imprintid'] in p['imprint'], pillfeatures))

    results = list(filter(lambda p: len(p['shapefeature']) == 7, results))
    
    # Save to tmp file
    tmpfilepath = os.path.join(os.getcwd(), str(uuid.uuid4()))
    open(tmpfilepath + '.tmp', mode='wb').write(base64.b64decode(img))

    # open tmp file
    with open(tmpfilepath + '.tmp', mode='rb') as f:
        with encoding2tmpfile.Encoding2TmpFile(base64.b64encode(f.read())) as tmpfile:
            labels = cx.getcx(tmpfile, svmmodel)

    os.remove(tmpfilepath + '.tmp')

    mrs = list(map(lambda p: MatchResult(sd.calc_cosine_similarity(hu, p['shapefeature']), p), results))

    sortedMrs = sorted(mrs, key=lambda m: m.probability, reverse=False)[:10]
    print(sortedMrs[0].pillfeature['name'], sortedMrs[0].pillfeature['strength'])
    print(sortedMrs[1].pillfeature['name'], sortedMrs[1].pillfeature['strength'])
    print(sortedMrs[2].pillfeature['name'], sortedMrs[2].pillfeature['strength'])

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
                        imprint=pillobj['imprint'],
                        colorfeature=cf,
                        shapefeature=sf
                    ).__dict__
                )
            except Exception:
                failed.append(f'{pillobj["name"]}, {pillobj["kind"]} {pillobj["strength"]}')
                continue

    logger.info(f'Finished calculating pillfeatures for {len(pillfeatures)} pills ({len(failed)} failed)') # noqa

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
        print(failed)