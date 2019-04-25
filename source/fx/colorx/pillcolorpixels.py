# pylint: disable=no-member, unsupported-assignment-operation
from typing import List

import cv2 as cv
import numpy as np
from colormath.color_objects import sRGBColor
 

def getcolorpixels(imagepath='resources/betolvex.jpg') -> List[sRGBColor]:
    c1, _ = shape_contour(imagepath)
    img1, _ = crop_image(imagepath, grayscale=False)

    # Add alpha component 
    img = cv.cvtColor(img1, cv.COLOR_RGB2RGBA)
    
    # Create a black layer in the size of the image (with RGBA values for pixels)
    mask: np.ndarray = np.zeros_like(img) 

    # Draw white on the mask layer where the pill is located (through the contour c1)
    cv.drawContours(mask, c1[0], 0, (255, 255, 255, 1), -1) 
    
    # Create a new layer and fill it with information from img in all pixels where the mask layer 
    # is white.
    out: np.ndarray = np.zeros_like(img) 
    out[mask == (255, 255, 255, 1)] = img[mask == (255, 255, 255, 1)]

    # Flatten the nD array of pixels into a 2D array of pixels with 4 values (RGBA).
    flatpixels: np.ndarray = out.flatten().reshape((-1, 4))

    # Filter out all pixels which are colored using nparray boolean index matching.
    # Basically we ignore all pixels with an alpha value of 0, as these belong to the mask layer.
    coloredpixels: np.ndarray = flatpixels[flatpixels[:, 0] != 0]

    # Finally, convert each pixel value to a sRGB colormath object, removing the alpha component
    result: List[sRGBColor] = []
    for pixel in coloredpixels:
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
def shape_contour(file): # pragma: no cover
    img1, img2 = crop_image(file)
    img1 = cv.GaussianBlur(img1, (5, 5), 0)
    img2 = cv.GaussianBlur(img2, (5, 5), 0)
    contour1 = get_contours(img1)
    contour2 = get_contours(img2)
    return contour1, contour2


def crop_image(file, grayscale=True): # pragma: no cover # noqa
    if not grayscale:
        img = cv.imread(file)
        lab = cv.cvtColor(img, cv.COLOR_RGB2LAB)
        lab_planes = cv.split(lab)
        clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        lab_planes[0] = clahe.apply(lab_planes[0])
        height, width = lab_planes[0].shape
        lab = cv.merge(lab_planes)
        img = cv.cvtColor(lab, cv.COLOR_LAB2RGB)
    else:
        img = cv.imread(file, 0)
        clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        img = clahe.apply(img)

        height, width = img.shape

    start_x1 = 60
    end_x1 = int(width / 2 - 35)
    start_x2 = int(width / 2 + 35)
    end_x2 = width - 60

    start_y = 60
    end_y = int(start_y + height - 90)

    crop_left = img[start_y: end_y, start_x1: end_x1]
    crop_right = img[start_y: end_y, start_x2: end_x2]

    return crop_left, crop_right


def get_contours(img): # pragma: no cover
    edges = cv.Canny(img, 200, 600)
    contours, hierarchy = cv.findContours(
        edges, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
    epsilon = 0.001*cv.arcLength(contours[0], True)
    approx = cv.approxPolyDP(contours[0], epsilon, True)
    return [approx], edges, hierarchy
