# pylint: disable=no-member, unsupported-assignment-operation
from typing import List

import cv2 as cv
import numpy as np
from colormath.color_objects import sRGBColor

from ..utils import showimg


def getcolorpixels(imagepath: str, skip: int, downscale: int) -> List[sRGBColor]:
    contours, _, _ = get_contours(cv.GaussianBlur(cv.imread(imagepath, 0), (5, 5), 0))

    # Add alpha component 
    img = cv.imread(imagepath)# , _ = cropproimg.crop_image(imagepath, grayscale=False)
    img = cv.cvtColor(img, cv.COLOR_RGB2BGRA)

    # Create a black layer in the size of the image (with RGBA values for pixels)
    mask: np.ndarray = np.zeros_like(img) 

    # Draw white on the mask layer where the pill is located (through the contour c1)
    cv.drawContours(mask, contours, 0, (255, 255, 255, 1), -1) 
    
    # Create a new layer and fill it with information from img in all pixels where the mask layer 
    # is white
    out: np.ndarray = np.zeros_like(img) 
    out[mask == (255, 255, 255, 1)] = img[mask == (255, 255, 255, 1)]

    # Resize image to 32x32 and then back to original size again in order to pixalate the image
    # We do this in order to reduce the number of unique pixels to 1024
    scaledout = cv.resize(out, (downscale, downscale), interpolation=cv.INTER_AREA)

    # showimg.showimgs(
    #     ['img', 'out', 'contourdrawing', 'scaled'],
    #     [img, out, showimg.get_contour_drawing(contours, edges, hierarchy), scaledout]
    # )
    # exit()

    # Flatten the nD array of pixels into a 2D array of pixels with 4 values (RGBA).
    flatpixels: np.ndarray = scaledout.flatten().reshape((-1, 4))

    # Filter out all pixels which are colored using nparray boolean index matching.
    # Basically we ignore all pixels with an alpha value of 0, as these belong to the mask layer.
    coloredpixels: np.ndarray = flatpixels[flatpixels[:, 0] != 0]

    # Finally, convert each pixel value to a sRGB colormath object, removing the alpha component
    result: List[sRGBColor] = []


    for index in range(0, len(coloredpixels)):
        if skip >= 0 and index % skip != 0:
            continue
        pixel = coloredpixels[index]
        result.append(
            sRGBColor(
                rgb_r=pixel[0], 
                rgb_g=pixel[1], 
                rgb_b=pixel[2],
                is_upscaled=True
            )
        )

    return result


# ####                               PETERS ALGO!                                ##### 
# SLET HERFRA NÅR DET ER IMPLEMENTERET I FX AF PETER OG BRUG DE IMPLEMENTATIONER I STEDET! #
def get_contours(img): # pragma: no cover
    edges = cv.Canny(img, 200, 600)
    contours, hierarchy = cv.findContours(edges, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
    epsilon = 0.0001*cv.arcLength(contours[0], True)
    approx = cv.approxPolyDP(contours[0], epsilon, True)
    
    return [approx], edges, hierarchy


