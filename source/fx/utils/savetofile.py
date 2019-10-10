import json
from ...repository import firestore

fbm = firestore.FBManager()


def parse(obj):
    if isinstance(obj, dict):
        return dicttype(obj)
    elif isinstance(obj, list):
        return listtype(obj)
    elif isinstance(obj, (str, float)):
        return obj
    elif isinstance(obj, bytes):
        return obj.decode('utf-8')
    else:
        print('Unknown parse: (Type:', type(obj), ')', obj)
        return obj


def dicttype(value):
    result = {}
    for k, v in value.items():
        result[k] = parse(v)

    return result


def listtype(value):
    result = []
    for elem in value:
        result.append(parse(elem))

    return result


def savemodel(model):
    result = {
        'svmmodel': model['svmmodel'].decode(encoding='latin1'),
        'pillfeatures': parse(model['pillfeatures'])
    }

    with open('resources/model.json', mode='w+') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)


def savepillstofile():
    allpills = fbm.get_all_pills_slim()
    with open('resources/allpills.json', mode='w+') as f:
        allpillslist = []
        for pillobj in allpills:
            pill = {}
            for k, v in pillobj.items():
                pill[k] = parse(v)

            allpillslist.append(pill)

        json.dump(allpillslist, f, indent=4, ensure_ascii=False)
        json.dump(allpills, f, indent=4)