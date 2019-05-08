import random as rng
import math

import numpy as np
import cv2 as cv


class ShapePreprocessor:
    def __init__(self):
        rng.seed(12345)

    def load_image_from_file(self, filePath):
        try:
            img = cv.samples.findFile(filePath)
        except Exception:
            raise Exception("Image could not be loaded from file")
        
        return img


    def crop_image(self, imgpath, grayscale=True): # pragma: no cover # noqa
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

        edges = cv.Canny(img, 100, 500)
        contours, hierarchy = cv.findContours(edges, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
        epsilon = 0.0001*cv.arcLength(contours[0], True)
        approx = cv.approxPolyDP(contours[0], epsilon, True)
        return [approx], edges, hierarchy

        
class ShapeDescriptor:
    def __init__(self):
        self.preprocessor = ShapePreprocessor()

    def calc_hu_moments_from_img(self, img):
        img, snd_img = self.preprocessor.crop_image(img)

        _, edges, _ = self.preprocessor.get_contours(img)
        _, snd_edges, _ = self.preprocessor.get_contours(snd_img)

        hu = self.calc_hu_moments(edges)
        snd_hu = self.calc_hu_moments(snd_edges)

        return hu, snd_hu

    def calc_hu_moments(self, edges):
        moments = cv.HuMoments(cv.moments(edges))

        # Log scaling
        huMoments = []
        for m in moments:
            huMoments.append(-1* math.copysign(1.0, m) * math.log10(abs(m)))

        return huMoments

    def calc_cosine_similarity(self, hu, snd_hu):
        # Convert to np arrays
        arr = np.array(hu)
        snd_arr = np.array(snd_hu)
        
        # Calculate the dot product and normalize
        dot = np.dot(arr, snd_arr)
        norm = np.linalg.norm(arr)
        snd_norm = np.linalg.norm(snd_arr)
    
        # Return the similarity
        return dot / (norm * snd_norm)