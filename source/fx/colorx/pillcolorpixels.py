# pylint: disable=no-member, unsupported-assignment-operation
import cv2 as cv
import numpy as np

# from ..utils import showimg
from ..shapex import ShapePreprocessor 


def getpillimagearray(imagepath: str) -> np.ndarray:
    # Read the image (grayscaled), blur it, erode it and get the contours
    contours, _, _ = ShapePreprocessor().get_contours(
        cv.erode(
            cv.GaussianBlur(
                cv.imread(imagepath, 0), 
                (5, 5), 
                0
            ), 
            np.ones((17, 17), np.uint8), 
            iterations=1
        )
    )

    # Read the image (with colors), add alpha-component, and add a blur (to smoothen the colors, 
    # remove color imperfections, and homogenize colors)
    img = cv.GaussianBlur(
        cv.cvtColor(
            cv.imread(imagepath),
            cv.COLOR_RGB2BGRA), 
            (5, 5), 
        0
    )
    
    # Create a black layer in the size of the image (with RGBA values for pixels)
    mask: np.ndarray = np.zeros_like(img) 

    # Draw white on the mask layer where the pill is located (through the contour c1)
    cv.drawContours(mask, contours, 0, (255, 255, 255, 1), -1) 
    
    # Create a new layer and fill it with information from img in all pixels where the mask layer 
    # is white
    out: np.ndarray = np.zeros_like(img) 
    out[mask == (255, 255, 255, 1)] = img[mask == (255, 255, 255, 1)]

    return cv.cvtColor(out, cv.COLOR_BGRA2BGR)


def getcolorpixels(src: np.ndarray) -> np.ndarray:
    # Erosion and dilation is implemented with inspiration from 
    # https://www.geeksforgeeks.org/erosion-dilation-images-using-opencv-python/
    kernel = np.ones((5, 5), np.uint8) 
    
    img_erosion = cv.erode(src, kernel, iterations=2) 
    img_dilation = cv.dilate(img_erosion, kernel, iterations=2)

    # Flatten the nD array of pixels into a 2D array of pixels with 3 values (RGB).
    flatpixels: np.ndarray = img_dilation.flatten().reshape((-1, 3))

    # Filter out all pixels which are colored using nparray boolean index matching.
    # Basically we ignore all pixels with an alpha value of 0, as these belong to the mask layer.
    coloredpixels: np.ndarray = flatpixels[flatpixels[:, 0] != 0]

    return coloredpixels


def grayscalecolorchannel(src: np.ndarray, channel: int):
    result = []
    for row in src:
        newrow = []
        for col in row:
            colorvalue = col[channel]
            newrow.append([*[np.uint8(colorvalue)]*3])
        result.append(np.array(newrow))
    
    return np.array(result)