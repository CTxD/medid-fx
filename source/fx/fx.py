from .colorx import cx
from .utils import encoding2img


def getmatches(imageencoding):
    return 'extract features for: ' + imageencoding 


def m(imageencoding: str, imagedescription: str = ''):
    with encoding2img.Encoding2IMG(imageencoding) as imgpath:
        cxoptions = {
            'raw_colormap': True,
            'xterm_colormap': True,
            'histogram': True,
            'verbose_desc': True,
            'delta_e': 1976,
            'colorbit': 6,
            'downscale': 64,
            'white_threshold': 10,
            'desc': imagedescription
        }
        cx.getcxmap(imgpath, **cxoptions)