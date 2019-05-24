import random as rng
import math
import base64

import numpy as np
import cv2 as cv
import copy
from .utils import showimg

from .utils import encoding2tmpfile
from sklearn.metrics.pairwise import cosine_similarity


class ShapePreprocessor:
    def __init__(self):
        rng.seed(12345)

    def convert_img_to_bytestring(self, img):
        retval, buffer = cv.imencode('.jpg', img)
        jpg_as_text = base64.b64encode(buffer)
        return jpg_as_text

    def load_image_from_file(self, filePath):
        try:
            img = cv.samples.findFile(filePath)
            img = cv.imread(img)

        except:
            raise Exception("Image could not be loaded from file")

        return img

    def load_image_from_bytestring(self, imgstring):
        try:
            with encoding2tmpfile.Encoding2TmpFile(imgstring) as tmpimg:
                img = cv.imread(tmpimg, 0)
        except:
            raise Exception("Image could not be decoded from bytestring")

        return img

    def load_image_from_bytestring_and_dims(self, imgstring, height, width):
        try:
            with encoding2tmpfile.Encoding2TmpFile(imgstring) as tmpimg:
                img = self.crop_before_matching(tmpimg, height, width)
        except:
            raise Exception("Image could not be decoded from bytestring")

        return img

    def grayscale_and_brightness(self, img):
        #clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        #img = clahe.apply(img)

        img = self.preprocess(img)
        
        #img = cv.GaussianBlur(img, (5, 5), 0)
        #img = cv.erode(img, np.ones((17, 17), np.uint8), iterations=1)
        #img = cv.bilateralFilter(img,9,60,20)

        return img

    def preprocess(self, img, gam = 3, bright = 336, totbright = 324, dim = 32, div = 8):
        lookUpTable = np.empty((1,256), np.uint8)
        for i in range(256):
            lookUpTable[0,i] = np.clip(pow(i / bright, gam) * totbright, 0, 255)
        img = cv.LUT(img, lookUpTable)

        kernel = np.ones((dim,dim),np.float32)/div
        img = cv.filter2D(img,-1,kernel)

        return img

    def crop_before_matching(self, imagepath, height, width):
        img = cv.imread(imagepath)

        tWidth = min(width, height)
        tHeight = max(width, height)

        width = tWidth
        height = tHeight
        if width < height:
            offset_y = height * -0.23
            rectSize = width * 0.4
            start_x = (width - rectSize) / 2
            start_y = (rectSize / 2 - offset_y)+100
            end_x = start_x + rectSize
            end_y = start_y + rectSize - 100
        else:
            offset_y = width * -0.23
            rectSize = height * 0.4
            start_x = (height - rectSize) / 2
            start_y = (rectSize / 2 - offset_y)+100
            end_x = start_x + rectSize
            end_y = start_y + rectSize - 100

        print(
            f'H/W: {height}/{width} -- X: ({start_x}, {end_x}), Y: ({start_y}, {end_y}), offset Y: {offset_y}')

        crop_img = img[int(start_y): int(end_y), int(start_x): int(end_x)]
        return crop_img

    def crop_image(self, imgpath, grayscale=True):  # pragma: no cover # noqa
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

    def get_contours(self, img):
        kernel = np.ones((7, 7), np.float32)/5
        img = cv.filter2D(img, -1, kernel)

        edges = cv.Canny(img, 200, 600)
        contours, hierarchy = cv.findContours(
            edges, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        if len(contours) > 0:
            epsilon = 0.001*cv.arcLength(contours[0], True)
            approx = cv.approxPolyDP(contours[0], epsilon, True)
            return [approx], edges, hierarchy
        return contours, edges, hierarchy

    def get_contours_test(self, img):

        edges = cv.Canny(img, 20, 510)
        contours, hierarchy = cv.findContours(
            edges, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        if len(contours) > 0:
            epsilon = 0.001*cv.arcLength(contours[0], True)
            approx = cv.approxPolyDP(contours[0], epsilon, True)
            return [approx], edges, hierarchy
        
        return contours, edges, hierarchy

 


class ShapeDescriptor:
    def __init__(self):
        self.preprocessor = ShapePreprocessor()

    def calc_hu_moments_from_single_img(self, img):
        c, edges, h = self.preprocessor.get_contours(img)


        d = showimg.get_contour_drawing(c, edges, h)
        d = cv.cvtColor(d, cv.COLOR_BGR2GRAY)

        hu = []
        if len(c) > 0:
            hu = self.calc_hu_moments(d)
        else:
            hu = [0, 0, 0, 0, 0, 0, 0]

        return hu

    def test_calc_hu_moments_from_single_img(self, img):
        c, edges, h = self.preprocessor.get_contours_test(img)

        d = showimg.get_contour_drawing(c, edges, h)
        d = cv.cvtColor(d, cv.COLOR_BGR2GRAY)
        hu = []
        if len(c) > 0:
            hu = self.calc_hu_moments(d)
        else:
            hu = [0, 0, 0, 0, 0, 0, 0]
        return hu, c

    def calc_hu_moments_from_img(self, img):
        img, snd_img = self.preprocessor.crop_image(img)

        c1, edges, _ = self.preprocessor.get_contours(img)
        c2, snd_edges, _ = self.preprocessor.get_contours(snd_img)

        hu = []
        snd_hu = []
        if len(c1) > 0:
            hu = self.calc_hu_moments(edges)
        if len(c2) > 0:
            snd_hu = self.calc_hu_moments(snd_edges)

        return hu, snd_hu

    def calc_hu_moments(self, edges):
        moments = cv.HuMoments(cv.moments(edges))

        # Log scaling
        huMoments = []
        for m in moments:
            if(m == 0.):
                continue
            huMoments.append(-1 * math.copysign(1.0, m) * math.log10(abs(m)))

        return huMoments

    def calc_cosine_similarity(self, hu, snd_hu):
        # Convert to np arrays
        arr = np.array(hu)
        snd_arr = np.array(snd_hu)
        distance = 0
        for i in range(6):
            distance += abs((1/arr[i] - 1/snd_arr[i]))


        distance = 0
        for i in range(6):
            distance += pow((arr[i]-snd_arr[i]), 2)
        math.sqrt(distance)
        return distance



        aa = arr.reshape(1, 7)
        ba = snd_arr.reshape(1, 7)
        cos_lib = cosine_similarity(aa, ba)
        return cos_lib[0][0]
