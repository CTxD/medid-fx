import numpy as np
import cv2

def crop(imagepath):
    img = cv2.imread(imagepath, 1)

    height, width, mode = img.shape
    offset_y = height * 0.1
    rectSize = width * 0.55

    start_x = width * 0.5 - rectSize / 2
    start_y = (height * 0.5 - rectSize / 2) - offset_y
    end_x = start_x + rectSize
    end_y = start_y + rectSize

    crop_img = img[int(start_y): int(end_y), int(start_x): int(end_x)]
    return crop_img
