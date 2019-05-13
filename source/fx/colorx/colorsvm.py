import json
import itertools as it
import csv 

import pandas as pd
from sklearn import svm, metrics
from sklearn.model_selection import train_test_split, cross_val_score

from ..utils import encoding2img
from .cx import getsvmvector


import warnings
warnings.filterwarnings("ignore")



def getfilteredpills(pills):
    ignorecolors = ['Spættet', 'Transparent']
    return list(filter(
        lambda x: len(x['color']) == 1 and x['color'][0] not in ignorecolors,
        pills
    ))


def train(pills): 
    svmvectorsdf = pd.DataFrame(getsvmvectors(pills))

    x = svmvectorsdf[
        [
            'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'F13', 'F14',
            'F15', 'F16', 'F17', 'F18', 'F19', 'F20'
        ]
    ]

    y = svmvectorsdf['Label']

    colorsvm = svm.SVC(max_iter=5000, kernel='rbf', C=900, gamma='scale')
    colorsvm.fit(x)

    return colorsvm


def getsvmvectors(pills):
    filteredpills = getfilteredpills(pills)

    svmvectors = []

    count = -1
    for pill in filteredpills:
        count += 1
        if count and count % 10 == 0:
            print(count / len(filteredpills) * 100, '%')

        if not pill['image'] or not pill['image'][0] or isinstance(pill['image'][0], dict):
            continue
      
        with encoding2img.Encoding2IMG(pill['image'][0]) as imagepath:
            try:
                pillsvmvector = getsvmvector(imagepath)
            except Exception:
                pass
            else:
                label = pill['color'][0] # For now we only handle single-color pills

                svmvectors.append({**pillsvmvector, 'Name': pill['name'], 'Label': label})
    
    return svmvectors


def predict(svmvector, pills):
    svmodel = train(pills)

    return svmodel.predict(svmvector)


def writecsvfile(svmvectors):
    csv_columns = ['Name', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8',
                   'F9', 'F10', 'F11', 'F12', 'F13', 'F14', 'F15',
                   'F16', 'F17', 'F18', 'F19', 'F20', 'Label']
    try:
        with open("resources/test_full.csv", 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in svmvectors:
                writer.writerow(data)

    except IOError:
        print("I/O error")


def test_best_accuracy_configuration_and_report():
    data = pd.read_csv("resources/test_full_compact.csv")
    x = data[
        [
            'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'F13', 'F14',
            'F15', 'F16', 'F17', 'F18', 'F19', 'F20'
        ]
    ]
    y = data['Label']

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=.2)

    settings = {
        'a_kernel': ['poly', 'rbf', 'sigmoid'],
        'b_gamma': ['scale'],
        'c_c': [5, 80, 900],
        # 'd_degree': [0],
        # 'e_coef': [0, 0.1],
    }
    allnames = sorted(settings)
    combinations = list(it.product(*(settings[Name] for Name in allnames)))

    bestconfig = ('', '', False)
    higestaccuracy = 0.0

    # for i in range(len(combinations)):
    #     comb = combinations[i]

    #     svc = svm.SVC(
    #         max_iter=5000, kernel=comb[0], gamma=comb[1], C=comb[2]
    #     )

    #     svc.fit(x_train, y_train)
    #     svc.predict(x_test)
    #     accuracy = svc.score(x_test, y_test)

    #     if accuracy > higestaccuracy:
    #         higestaccuracy = accuracy
    #         bestconfig = comb
    #     print("Configuration: " + str(comb) + " || Accuracy: " + str(accuracy))
    

    man = svm.SVC(max_iter=5000, kernel='rbf', C=900, gamma='scale')
    
    scores = cross_val_score(man, x, y, cv=10)
    #print(scores)
    #print(bestconfig, higestaccuracy)

    print_accuracy_report(man, x,y, 10)

def print_accuracy_report(classifier, X, y, num_validations=5):
    accuracy = cross_val_score(classifier, 
            X, y, scoring='accuracy', cv=num_validations)
    print("Accuracy: " + str(round(100*accuracy.mean(), 2)) + "%")

    f1 = cross_val_score(classifier, 
            X, y, scoring='f1_weighted', cv=num_validations)
    print ("F1: " + str(round(100*f1.mean(), 2)) + "%")

    precision = cross_val_score(classifier, 
            X, y, scoring='precision_weighted', cv=num_validations)
    print ("Precision: " + str(round(100*precision.mean(), 2)) + "%")

    recall = cross_val_score(classifier, 
            X, y, scoring='recall_weighted', cv=num_validations)
    print ("Recall: " + str(round(100*recall.mean(), 2)) + "%")  