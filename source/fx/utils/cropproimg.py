# pylint: disable=no-member, unsupported-assignment-operation
import cv2 as cv

def crop_image(imgpath, grayscale=True): # pragma: no cover # noqa
    """
    Takes as input the path to a pro.medicin.dk image and returns the two cropped images as numpy
    arrays.

    Crops out the ruler on the image and splits the image in two through the middle.
    """
    clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    
    if grayscale:
        img = cv.imread(imgpath, 0)
        img = clahe.apply(img)
        height, width = img.shape
        img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
    else:
        img = cv.imread(imgpath)
        lab = cv.cvtColor(img, cv.COLOR_RGB2LAB)
        lab_planes = cv.split(lab)
        lab_planes[0] = clahe.apply(lab_planes[0])
        height, width = lab_planes[0].shape
        lab = cv.merge(lab_planes)
        img = cv.cvtColor(lab, cv.COLOR_LAB2BGR)

    start_x1 = 25
    end_x1 = int(width / 2)
    start_x2 = int(end_x1 + 5)
    end_x2 = int(width - 25)

    start_y = 45
    end_y = int(start_y + height - 65)

    crop_left = img[start_y: end_y, start_x1: end_x1]
    crop_right = img[start_y: end_y, start_x2: end_x2]

    return crop_left, crop_right