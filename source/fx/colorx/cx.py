import os
import collections
import time
import logging

from typing import List

from colormath.color_objects import sRGBColor
from .pillcolorpixels import getcolorpixels
from .colormap import convert_pixel_colors_to_vector
from ..utils import colorheatmap, histogram
from ...config import CONFIG


logger = logging.getLogger(__name__)
# Train model, skal tage en encoding af et pro.medicin billede, åbne det, croppe det og gemme de to encodings separat


def getcxmap(imagepath: str, **options): # noqa
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
            If true the settings for skip, colorbit, delta_e, and scaling will be suffixed to 
            <imagepath name>

    Output files are *NOT* generated on PROD environments!

    Output files are saved to <root>/output/<imagepath name>/. 
    Default naming convention is <imagepath name>_<output type>.<imagepath extension>
        E.g. histogram for somepill.jpg is saved as somepill_histogram.jpg
    If desc is provided, the desc will replace the <imagepath name>.

    Passed-through options:
        - downscale: int >= 32 (getcolorpixels)
            Determines size of the image when downscaling. Image will be downsized to a square of 
            size <downscale>x<downscale>. 
        - skip: int >= 0 (getcolorpixels)
            Only takes every <skip> pixel from the image.
        - colorbit: int [6|8] (colormap)
            Which color palette to use. Choose between 6 and 8 bit palettes.
        - delta_e: int [1976|1994|2000] (colormap)
            Which delta_e algorithm to use. Choose between 1976, 1994, and 2000.
    """
    starttime = time.time()

    colorbit = 6
    if 'colorbit' in options and options['colorbit'] in (6, 8):
        colorbit = options['colorbit']

    delta_e = 1976
    if 'delta_e' in options and options['delta_e'] in (1976, 1994, 2000):
        delta_e = options['delta_e']

    skip = 2
    if 'skip' in options and isinstance(options['skip'], int) and options['skip'] >= 0:
        skip = options['skip']    

    downscale = 36
    if 'downscale' in options and isinstance(options['downscale'], int) and options['downscale'] >= 32: # noqa
        downscale = options['downscale']  

    imgname, extension = os.path.basename(imagepath).split('.')
    if 'desc' in options and options['desc'] and isinstance(options['desc'], str):
        imgname = options['desc']
    
    if 'verbose_desc' in options and isinstance(options['verbose_desc'], bool) and options['verbose_desc']: # noqa
        imgname = f'{imgname}_skip{skip}_bit{colorbit}_deltae{delta_e}_dscale{downscale}'

    pixels = getcolorpixels(imagepath, skip, downscale)

    hex_raw = [pixel.get_rgb_hex() for pixel in pixels]
    hex_count = collections.Counter(hex_raw)
    print(len(pixels), len(hex_count))
     
    xterm_raw = convert_pixel_colors_to_vector(hex_count, colorbit, delta_e)
    total = sum(xterm_raw.values())
    xterm_weighted = {color: ((1/total)*count*100) for color, count in xterm_raw.items()}
    endtime = time.time()
    print('Delta time:', str(endtime - starttime), 'seconds')

    if 'raw_colormap' in options and options['raw_colormap'] and CONFIG['ENVIRONMENT'] == 'DEV':
        filepath = f'output/{imgname}_raw_colormap.{extension}'
        logger.debug(f'Saving raw colormap to: {filepath}')
        colorheatmap.img_creater(pixels, 'RGB', 20, filepath)

    if 'xterm_colormap' in options and options['xterm_colormap'] and CONFIG['ENVIRONMENT'] == 'DEV':
        filepath = f'output/{imgname}_xterm_colormap.{extension}'
        logger.debug(f'Saving xterm colormap to: {filepath}')
        xtermrgb: List[sRGBColor] = []
        for color, count in xterm_raw.items():
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

    if 'histogram' in options and options['histogram'] and CONFIG['ENVIRONMENT'] == 'DEV':
        filepath = f'output/{imgname}_histogram.{extension}'
        logger.debug(f'Saving histogram to: {filepath}')
        histogram.createhistogram(xterm_weighted, filepath, colorbit)
