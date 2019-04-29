import numpy as np
import cv2 as cv
import random as rng
import math


class ShapePreprocessor:
    def __init__(self):
        rng.seed(12345)

    def load_image_from_file(self, filePath):
        try:
            img = cv.samples.findFile(filePath)
        except:
            raise Exception("Image could not be loaded from file")
        
        return img

    def load_image_from_bytestring(self, imgstring):
        try:
            nparr = np.fromstring(imgstring, np.uint8)
            img = cv.imdecode(nparr, cv.IMREAD_COLOR)
        except:
            raise Exception("Image could not be decoded from bytestring")
        
        return img

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

    def get_contours(self, img):
        edges = cv.Canny(img, 200, 600)
        contours, hierarchy = cv.findContours(edges, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
        epsilon = 0.001*cv.arcLength(contours[0], True)
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