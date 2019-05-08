# pylint: disable=no-member, unsupported-assignment-operation
from typing import List

import cv2 as cv
import numpy as np
from colormath.color_objects import sRGBColor

from ..utils import showimg
from ..shapex import ShapePreprocessor 


def getcolorpixels(imagepath: str, downscale: int) -> List[np.array]:
    out = _extractpill(imagepath)

    coloredpixels = processpillimage(out, downscale)

    return coloredpixels


def _extractpill(imagepath: str) -> np.ndarray:
    blurimg = cv.GaussianBlur(cv.imread(imagepath, 0), (5, 5), 0)

    erodedblurimg = cv.erode(blurimg, np.ones((17, 17), np.uint8), iterations=1)

    contours, _, _ = ShapePreprocessor().get_contours(erodedblurimg)

    # Add alpha component 
    img = cv.imread(imagepath)
    img = cv.cvtColor(img, cv.COLOR_RGB2BGRA)

    # Create a black layer in the size of the image (with RGBA values for pixels)
    mask: np.ndarray = np.zeros_like(img) 

    # Draw white on the mask layer where the pill is located (through the contour c1)
    cv.drawContours(mask, contours, 0, (255, 255, 255, 1), -1) 
    
    # Create a new layer and fill it with information from img in all pixels where the mask layer 
    # is white
    out: np.ndarray = np.zeros_like(img) 
    out[mask == (255, 255, 255, 1)] = img[mask == (255, 255, 255, 1)]

    return out


def processpillimage(src: np.ndarray, downscale: int) -> np.ndarray:
    # Erosion and dilation is implemented with inspiration from 
    # https://www.geeksforgeeks.org/erosion-dilation-images-using-opencv-python/
    kernel = np.ones((5, 5), np.uint8) 
    
    img_erosion = cv.erode(src, kernel, iterations=2) 
    img_dilation = cv.dilate(img_erosion, kernel, iterations=2)
    
    # Resize image to 32x32 and then back to original size again in order to pixalate the image
    # We do this in order to reduce the number of unique pixels to 1024
    scaledout = cv.resize(img_dilation, (downscale, downscale), interpolation=cv.INTER_AREA)
    
    # Flatten the nD array of pixels into a 2D array of pixels with 4 values (RGBA).
    flatpixels: np.ndarray = scaledout.flatten().reshape((-1, 4))

    # Filter out all pixels which are colored using nparray boolean index matching.
    # Basically we ignore all pixels with an alpha value of 0, as these belong to the mask layer.
    coloredpixels: np.ndarray = flatpixels[flatpixels[:, 0] != 0]

    return coloredpixels


def grayscalecolorchannel(src: np.ndarray, index: int):
    result = []
    for row in src:
        newrow = []
        for col in row:
            colorvalue = col[index]
            newrow.append([
                np.uint8(colorvalue),
                np.uint8(colorvalue),
                np.uint8(colorvalue),
                np.uint8(col[3])
            ])
        result.append(np.array(newrow))
    
    return np.array(result)