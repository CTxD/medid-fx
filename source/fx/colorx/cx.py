import colorsys
import warnings
import pickle
from typing import List, Dict

import numpy as np
import pandas as pd
from sklearn import svm

from .pillcolorpixels import getcolorpixels, getpillimagearray
from ..utils import encoding2tmpfile
from ...repository import firestore


warnings.filterwarnings("ignore")


def getcx(imagepath: str) -> List[str]: 
    svmvector = getsvmvector(imagepath)
    
    # Fetch latest svmmodel from db and convert it to an SVC object
    svmmodel: svm.SVC = pickle.loads(firestore.FBManager().get_latest_model()['svmmodel']) 
    
    return svmmodel.predict([[v for _, v in svmvector.items()]]) 


def getsvmvectors(pills: List[Dict]) -> List[Dict[str, float]]:
    svmvectors = []

    count = -1
    for pill in pills:
        count += 1
        if count and count % 100 == 0:
            print(count / len(pills) * 100, '%')

        if not pill['image'] or not pill['image'][0] or isinstance(pill['image'][0], dict):
            continue

        with encoding2tmpfile.Encoding2TmpFile(pill['image'][0]) as imagepath:
            try:
                pillsvmvector = getsvmvector(imagepath)
            except Exception:
                pass
            else:
                # For now we only handle single-color pills
                label = compreslabels(pill['color'])[0]

                svmvectors.append(
                    {**pillsvmvector, 'Name': pill['name'], 'Label': label})

    return svmvectors


def getsvmvector(imagepath: str) -> Dict[str, float]:
    svmvector: Dict[str, float] = {f'F{i}': 0.0 for i in range(1, 21)}

    imgarray = getpillimagearray(imagepath)
    imgpixels = getcolorpixels(imgarray)

    rgbstddev = np.std(imgpixels, axis=0)
    rgbavg = np.average(imgpixels, axis=0)
    for index, avg in enumerate(rgbavg):
        # Features 1-3; Red, Green, and Blue intensity
        svmvector[f'F{index+1}'] = avg
    
        # Features 4-6; Std. Dev for Red, Green, and Blue intensity
        svmvector[f'F{index+4}'] = rgbstddev[index]
 
    hsvpixels = np.array([colorsys.rgb_to_hsv(pixel[0], pixel[1], pixel[2]) for pixel in imgpixels])
    hsvstddev = np.std(hsvpixels, axis=0)
    for index, avg in enumerate(np.average(hsvpixels, axis=0)):
        # Features 7-9; Hue, Saturaion, Value mean  
        svmvector[f'F{index+7}'] = avg

        # Features 10-12; Std. Dev. for Hue, Saturation, and Value
        svmvector[f'F{index+10}'] = hsvstddev[index]

    # Features 13-16; Red, Green, Blue, and Yellow Chromaticity mean
    rgbvalsum = sum(rgbavg)
    svmvector['F13'] = rgbavg[0]/(rgbvalsum)
    svmvector['F14'] = rgbavg[1]/(rgbvalsum)
    svmvector['F15'] = rgbavg[2]/(rgbvalsum)
    svmvector['F16'] = (rgbavg[0]+rgbavg[1])/(2*rgbvalsum)

    # Features 17-18; RG, GB, BR averages
    svmvector['F17'] = (rgbavg[0]+rgbavg[1])/2
    svmvector['F18'] = (rgbavg[1]+rgbavg[2])/2
    svmvector['F19'] = (rgbavg[2]+rgbavg[0])/2

    # Feature 20; Brightness / mean intensity
    svmvector['F20'] = rgbvalsum/3 

    return svmvector


def train(pills: List[Dict]) -> svm.SVC:
    svmvectorsdf = pd.DataFrame(getsvmvectors(pills))

    x = svmvectorsdf[
        [
            'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'F13', 'F14',
            'F15', 'F16', 'F17', 'F18', 'F19', 'F20'
        ]
    ]

    y = svmvectorsdf['Label']

    colorsvm = svm.SVC(max_iter=5000, kernel='rbf', C=900, gamma='scale')
    colorsvm.fit(x, y)

    return colorsvm


_labelmappings = {
    'Gul': ['Lysegul', 'Gul', 'Mørkegul'],
    'Rød': ['Lyserød', 'Rød', 'Mørkerød'],
    'Brun': ['Lysebrun', 'Brun', 'Mørkebrun'],
    'Grøn': ['Lysegrøn', 'Grøn', 'Mørkegrøn'],
    'Blå': ['Lysbelå', 'Blå', 'Mørkeblå'],
    
    'Grå': ['Grå', 'Lysegrå'],
    'Orange': ['Orange', 'Lys orange'],
    'Fersken': ['Fersken', 'Lys fersken'],
    'Lilla': ['Lilla', 'Lys lilla'],

    'Rødbrun': ['Rødbrun'],
    'Hvid': ['Hvid'],
    'Rosa': ['Rosa'],
    'Beige': ['Beige'],
    'Sort': ['Sort'],
    'Grågrøn': ['Grågrøn'],
    'Pink': ['Pink'],
    'Turkis': ['Turkis'],
    'Offwhite': ['Offwhite'],
    'Gråbrun': ['Gråbrun'],
    'Gråhvid': ['Gråhvid'],

    'Gennemsigtig': ['Gennemsigtig'],
    'Transparent': ['Transparent'],
    'Spættet': ['Spættet'],
}


def compreslabels(labels: List[str]) -> List[str]:
    compmap = {label: comp for comp, labellist in _labelmappings.items() for label in labellist}
    result: List[str] = []
    for label in labels:
        if label not in compmap:
            continue
        result.append(compmap[label])

    return result


def uncompreslabels(labels: List[str]) -> List[str]:
    result: List[str] = []
    for label in labels:
        if label not in _labelmappings:
            continue
        result.extend(_labelmappings[label])

    return result