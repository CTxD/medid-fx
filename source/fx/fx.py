import csv

from .colorx import cx, colorsvm
from .utils import encoding2img, promedimgsplit
from ..repository import firestore


def getmatches(imageencoding):
    return 'extract features for: ' + imageencoding 


def m(imageencoding: str, imagedescription: str = ''):
    with encoding2img.Encoding2IMG(imageencoding) as imgpath:
        cxoptions = {
            'raw_colormap': True,
            'xterm_colormap': False,
            'histogram': False,
            'verbose_desc': True,
            'delta_e': 1976,
            'colorbit': 6,
            'downscale': 64,
            'white_threshold': 10,
            'desc': imagedescription
        }
        cx.getcxmap(imgpath, **cxoptions)


def train():
    # mockpill = {
    #     'name': 'Mock pill',
    #     'substance': 'Mockamol',
    #     'kind': 'Tablet',
    #     'strength': '100 mg',
    #     'imprint': [],
    #     'score': '',
    #     'color': ['Lyseblå'],
    #     'size': '100x100',
    #     'image': open('resources/furixretard_encoding', mode='rb').read()
    # }

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

    # Train SVM
    res = colorsvm.predict(['WhateverName',170.7451684152402,196.6902263942573,210.11830480397572,4.877595882428889,3.1138188824459823,3.3679559245548476,0.5569988081056207,0.18753089499055584,210.11830480397572,0.004698496351695571,0.011381744333048994,3.3679559245548476,0.2956351392597971,0.3405574694195395,0.36380739132066336,0.3180963043396683,183.71769740474875,203.4042655991165,190.43173660960795,192.51789987115774], allpills)
    print(res)
    
    # svmmodel = colorsvm.train(allpills)
    exit()
    # Train model
    #for pillobj in allpills:
        # Get shape vector
        # Get color vector
        # combine

        # Add to matrix

    # Upload model + SVM model

def parse(obj):
    if isinstance(obj, dict):
        return dicttype(obj)
    elif isinstance(obj, list):
        return listtype(obj)
    elif isinstance(obj, str):
        return obj 
    elif isinstance(obj, bytes):
        return obj.decode('utf-8')
    else:
        print('Unknown parse: (Type:', type(obj), ')', obj)
        return obj


def dicttype(value):
    result = {}
    for k, v in value.items():
        result[k] = parse(v)

    return result


def listtype(value): 
    result = []
    for elem in value:
        result.append(parse(elem))

    return result


def savetofile():
    import json
    allpills = fbm.get_all_pills_slim()
    with open('resources/allpills2.json', mode='w+') as f:
        allpillslist = []
        for pillobj in allpills:
            pill = {}
            for k, v in pillobj.items():
                pill[k] = parse(v)
            
            allpillslist.append(pill)

        json.dump(allpillslist, f, indent=4, ensure_ascii=False)
        json.dump(allpills, f, indent=4)