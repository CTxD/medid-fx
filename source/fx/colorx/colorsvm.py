from sklearn import svm
from sklearn.model_selection import train_test_split

from ..utils import encoding2img
from .cx import getsvmvector


def train(pills): 
    svmvectors = []
    labels = []

    for pill in pills:
        with encoding2img.Encoding2IMG(pill['image'][0]) as imagepath:
            pillsvmvector = getsvmvector(imagepath)
            label = pill['color'][0] # For now we only handle single-color pills

            svmvectors.append(pillsvmvector)
            labels.append(label)

      
    svc = svm.LinearSVC()
    vector_train, vector_test, label_train, label_test = train_test_split(svmvectors, labels)
