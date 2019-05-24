import base64
import os
import copy

import cv2 as cv

from ..shapex import ShapePreprocessor
from .encoding2tmpfile import Encoding2TmpFile


def promedimgsplit(pillobj):
    with Encoding2TmpFile(pillobj['image'][0]) as promedimgpath:
        objs = {}
        objs['left_img'], objs['right_img'] = ShapePreprocessor().crop_image(
            promedimgpath, 
            grayscale=False
        )
        
        tmpimgname, tmpimgext = os.path.basename(promedimgpath).split('.')
        tmpimgpath = os.path.dirname(promedimgpath)
        for side in ('left', 'right'):
            imgpath = os.path.join(tmpimgpath, f'{tmpimgname}_{side}.{tmpimgext}')

            cv.imwrite(imgpath, cv.cvtColor(objs[side + '_img'], cv.COLOR_RGB2BGRA))
            
            objs[side + '_pill'] = copy.deepcopy(pillobj)
            objs[side + '_pill']['image'] = [base64.b64encode(open(imgpath, mode='rb').read())]
            objs[side + '_pill']['side'] = side

    return objs['left_pill'], objs['right_pill']
