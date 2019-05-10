from .colorx import cx, colorsvm
from .utils import encoding2img
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
    fbm = firestore.FBManager()

    singlecolorpills = list(filter(
        lambda x: len(x['color']) == 1,
        fbm.get_all_pills_slim()
    ))

    colorsvm.train(singlecolorpills)
    
