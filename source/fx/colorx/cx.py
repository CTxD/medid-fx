from .pillcolorpixels import getcolorpixels
from ...utils import colormap


def main():
    pillname = 'betolvex'
    res = getcolorpixels(f'resources/{pillname}.jpg')
    print(len(res))
    colormap.img_creater(res, 20, f'output/{pillname}_colormap')