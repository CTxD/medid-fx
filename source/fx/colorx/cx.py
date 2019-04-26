from .pillcolorpixels import getcolorpixels
from ...utils import colormap

def main():
    res = getcolorpixels('resources/betolvex.jpg')
    colormap.img_creater(res, 5, 'betolvex_colormap')