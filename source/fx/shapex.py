import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
import random as rng
import math
from scipy.spatial.distance import cdist, cosine
from scipy.optimize import linear_sum_assignment

class ShapePreprocessor:
    def __init__(self):
        rng.seed(12345)

    def load_image_from_file(self, filePath):
        return cv.samples.findFile(filePath)

    def crop_image(self, img):
        img = cv.imread(img, 0)
        clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        img = clahe.apply(img)

        height, width = img.shape

        start_x1 = 25
        end_x1 = int(width / 2)
        start_x2 = end_x1 + 5
        end_x2 = width - 25

        start_y = 45
        end_y = int(start_y + height - 65)

        crop_left = img[start_y: end_y, start_x1: end_x1]
        crop_right = img[start_y: end_y, start_x2: end_x2]

        return crop_left, crop_right

    def shape_contour(self, img):
        img1, img2 = crop_image(img)
        img1 = cv.GaussianBlur(img1, (5, 5), 0)
        img2 = cv.GaussianBlur(img2, (5, 5), 0)
        
        contour1 = get_contours(img1)
        contour2 = get_contours(img2)
        
        return contour1, contour2

    def get_contours(self, img):
        edges = cv.Canny(img, 200, 600)
        contours, hierarchy = cv.findContours(edges, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
        epsilon = 0.001*cv.arcLength(contours[0], True)
        approx = cv.approxPolyDP(contours[0], epsilon, True)

        return [approx], edges, hierarchy

class ShapeDescriptor:
    def __init__(self):
        self.preprocessor = ShapePreprocessor()

    def calc_hu_moments_from_img(img):
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
        arr = np.array(hu)
        snd_arr = np.array(snd_hu)

        dot = np.dot(arr, snd_arr)
        norm = np.linalg.norm(arr)
        snd_norm = np.linalg.norm(snd_arr)
    
        return dot / (norm * snd_norm)

shape_descriptor = ShapeDescriptor()
shape_processor = ShapePreprocessor()

img = shape_processor.load_image_from_file("../images/1.jpg")

hu, snd_hu = shape_descriptor.calc_hu_moments_from_img(img)
print("Hu: ", hu, snd_hu)
print("Sim: ", shape_descriptor.calc_cosine_similarity(hu, snd_hu))