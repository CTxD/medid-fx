# pylint: disable=no-member, unsupported-assignment-operation
import random as rng

import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt

rng.seed(12345)


def showimgs(titles, images): # pragma: no cover
    if not isinstance(titles, list):
        titles = [titles]
    
    if not isinstance(images, list):
        images = [images]

    for i in range(len(images)): # noqa
        plt.subplot(2, 2, i+1)
        plt.imshow(images[i])
        plt.title(titles[i])
        plt.xticks([])
        plt.yticks([])
    plt.show()


def get_contour_drawing(contours, edges, hierarchy):
    drawing = np.zeros((edges.shape[0], edges.shape[1], 3), dtype=np.uint8)
    for i in range(len(contours)): # noqa
        epsilon = 0.01*cv.arcLength(contours[i], True)
        approx = cv.approxPolyDP(contours[i], epsilon, True)
        color = (rng.randint(0, 256), rng.randint(0, 256), rng.randint(0, 256))
        cv.drawContours(drawing, contours, i, color,
                        2, cv.LINE_8, hierarchy, 0)
    return drawing