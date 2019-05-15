import csv
import pandas as pd

from .colorx import cx, colorsvm
from .utils import encoding2img, promedimgsplit
from ..repository import firestore

import base64
import requests


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
    # allpills = []
    # for pillobj in fbm.get_all_pills_slim():
    #     if not pillobj['image'] or isinstance(pillobj['image'][0], dict):
    #         continue

    #     pillobj['image'][0] = bytes(pillobj['image'][0], encoding='utf-8')
    #     allpills.extend(promedimgsplit.promedimgsplit(pillobj))

    # dicct = {
    #     "F1": 100,
    #     "F2": 20,
    #     "F3": 3333,
    #     "F4": 100,
    #     "F5": 20,
    #     "F6": 3333,
    #     "F7": 100,
    #     "F8": 20,
    #     "F9": 3333,
    #     "F10": 100,
    #     "F11": 20,
    #     "F12": 3333,
    #     "F13": 100,
    #     "F14": 20,
    #     "F15": 3333,
    #     "F16": 100,
    #     "F17": 20,
    #     "F18": 3333,
    #     "F19": 33,
    #     "F20": 22
    # }

    def get_as_base64(url):
        return str(base64.b64encode(requests.get(url).content))

    allpills = fbm.get_all_pills_slim()

    pill_map_dict = {}

    for pill in allpills:
        print(pill['name'])
        if len(pill['imprint']) == 0:
            continue
        if pill['imprint'] == "":
            continue
        if pill['imprint'][0].startswith("/res"):
            if pill['imprint'][0] in pill_map_dict.keys():
                continue
            else:
                pill_map_dict[pill['imprint'][0]] = get_as_base64(
                    "http://pro.medicin.dk" + pill['imprint'][0])

    print(pill_map_dict)
    import json
    with open('peterpikhaar.txt', 'w') as file:
        file.write(json.dumps(pill_map_dict, indent=4))

    # Train model
    # for pillobj in allpills:
    # Get shape vector
    # Get color vector
    # combine0

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
