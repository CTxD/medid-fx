import os
import time
import logging
import json
import colorsys
from typing import List, Dict

import numpy as np

from colormath.color_objects import sRGBColor
from .pillcolorpixels import getcolorpixels, getpillimagearray, grayscalecolorchannel
from .colormap import convert_pixel_colors_to_vector
from ..utils import colorheatmap, histogram, showimg
from ...config import CONFIG


logger = logging.getLogger(__name__)


def getcxmap(imagepath: str, **optionskwargs): 
    """
    Supported options:
        - raw_colormap: bool
            Create a colormap of the raw pixels. 
        - xterm_colormap: bool
            Create a colormap of the xterm mapped colors.
        - histogram: bool 
            Make a histogram of the xterm mapped colors.
        - desc: str
            Description of the pill (keep it short). Overrides nameing convention of 
            output files. Useful for identifying output files in bulk runs.
        - verbose_desc: bool
            If true the settings for colorbit, delta_e, and scaling will be suffixed to 
            <imagepath name>

    Output files are *NOT* generated on PROD environments!

    Output files are saved to <root>/output/<imagepath name>/. 
    Default naming convention is <imagepath name>_<output type>.<imagepath extension>
        E.g. histogram for somepill.jpg is saved as somepill_histogram.jpg
    If desc is provided, the desc will replace the <imagepath name>.

    Passed-through options:
        - colorbit: int [6|8] (colormap)
            Which color palette to use. Choose between 6 and 8 bit palettes.
        - delta_e: int [1976|1994|2000] (colormap)
            Which delta_e algorithm to use. Choose between 1976, 1994, and 2000.
        - white_threshold: int
    """
    starttime = time.time()
    # options = extractparameters(**{**optionskwargs, 'imagepath': imagepath})

    svmvector = getsvmvector(imagepath)

    print(json.dumps(svmvector, indent=4))
    endtime = time.time()
    
    print('Delta time:', str(endtime-starttime), " seconds")

    # outputimages(**{**options, 'pixels': pixels, 'xterm_raw': xterm_raw, 'xterm_weighted': xterm_weighted}) # noqa


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


def outputimages(**kwargs):    
    if kwargs['raw_colormap']:
        filepath = f'output/{kwargs["imgname"]}_raw_colormap.{kwargs["extension"]}'
        logger.debug(f'Saving raw colormap to: {filepath}')
        colorheatmap.img_creater(kwargs['pixels'], 'RGB', 20, filepath)

    if kwargs['xterm_colormap']:
        filepath = f'output/{kwargs["imgname"]}_xterm_colormap.{kwargs["extension"]}'
        logger.debug(f'Saving xterm colormap to: {filepath}')
        xtermrgb: List[sRGBColor] = []
        for color, count in kwargs['xterm_raw'].items():
            xtermrgb.extend(
                list(
                    map(
                        lambda x: sRGBColor.new_from_rgb_hex(x), 
                        [color]*count
                    )
                )
            )
        # for index in range(0, len(xterm)): # noqa
        #     if xterm[index] == 0:
        #         continue

        #     for _ in range(0, xterm[index]):
        #         xtermrgb.append(sRGBColor.new_from_rgb_hex(hex_values[index]))
        colorheatmap.img_creater(xtermrgb, 'RGB', 20, filepath)

    if kwargs['histogram']:
        filepath = f'output/{kwargs["imgname"]}_histogram.{kwargs["extension"]}'
        logger.debug(f'Saving histogram to: {filepath}')
        histogram.createhistogram(kwargs['xterm_weighted'], filepath, kwargs['colorbit'])


def extractparameters(**options):
    colorbit = 6
    if 'colorbit' in options and options['colorbit'] in (3, 6, 8):
        colorbit = options['colorbit']

    delta_e = 1976
    if 'delta_e' in options and options['delta_e'] in (1976, 1994, 2000):
        delta_e = options['delta_e']

    white_threshold = 0
    if 'white_threshold' in options and isinstance(options['white_threshold'], int):
        white_threshold = options['white_threshold']  

    imgname, extension = os.path.basename(options['imagepath']).split('.')
    if 'desc' in options and options['desc'] and isinstance(options['desc'], str):
        imgname = options['desc']
    
    if 'verbose_desc' in options and isinstance(options['verbose_desc'], bool) and options['verbose_desc']: # noqa
        imgname = f'{imgname}_bit{colorbit}_deltae{delta_e}'

    raw_colormap = 'raw_colormap' in options and options['raw_colormap'] and CONFIG['ENVIRONMENT'] == 'DEV' # noqa

    xterm_colormap = 'xterm_colormap' in options and options['xterm_colormap'] and CONFIG['ENVIRONMENT'] == 'DEV' # noqa

    histogram = 'histogram' in options and options['histogram'] and CONFIG['ENVIRONMENT'] == 'DEV'

    return {
        'colorbit': colorbit,
        'delta_e': delta_e,
        'white_threshold': white_threshold,
        'imgname': imgname,
        'extension': extension,
        'raw_colormap': raw_colormap,
        'xterm_colormap': xterm_colormap,
        'histogram': histogram
    }

