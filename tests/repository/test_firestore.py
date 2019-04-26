# pylint:disable=protected-access
import mockfirestore

from source.models.v1 import pill


# Helper
def _convert_obj_to_dict(obj):
    class_dict = {}
    for attr in dir(obj):
        if attr.startswith('__'):
            continue

        attrvalue = getattr(obj, attr)

        if callable(attrvalue):
            continue

        if isinstance(attrvalue, list):
            newattrvalue = []
            for oldvalue in attrvalue:
                newattrvalue.append(_convert_obj_to_dict(oldvalue))

            attrvalue = newattrvalue

        class_dict[attr] = attrvalue

    return class_dict


def mock_data(firebasemanager):
    firebasemanager.db = mockfirestore.MockFirestore()
    firebasemanager.db.reset()

    pics_1 = pill.PhotoIdentification(
        'Filmovertrukne tabletter  500 mg  (novum)',
        '/resource/media/37171ea6-9e38-473a-b491-00cadae42273',
        'Ingen kærv',
        '200 mg',
        'Gul',
        '8,8 x 18,8',
        '/resource/media/C9697D2P?ptype=1'
    )
    pics_2_1 = pill.PhotoIdentification(
        'Filmovertrukne tabletter  500 mg',
        '/resource/media/15fb56d9-856a-4352-bb83-bca96eea9d09',
        'Ingen kærv',
        '200 mg',
        'Hvid',
        '9 x 18,8',
        '/resource/media/MSUC458E?ptype=1'
    )
    photos_1 = [pics_1, pics_2_1]
    pill_1 = pill.PillData(photos_1, "Abboticin", "Erythromycin")

    pics_2 = pill.PhotoIdentification(
        'Filmovertrukne tabletter  500 mg  (novum)',
        'nothing',
        'Ingen kærv',
        '200 mg',
        'Gul',
        '8,8 x 18,8',
        '/resource/media/C9697D2P?ptype=1'
    )
    pics_2_2 = pill.PhotoIdentification(
        'Filmovertrukne tabletter  500 mg',
        'nothing',
        'Ingen kærv',
        '200 mg',
        'Hvid',
        '9 x 18,8',
        '/resource/media/MSUC458E?ptype=1'
    )
    photos_2 = [pics_2, pics_2_2]
    pill_2 = pill.PillData(photos_2, "Viagra", "Villigril")

    converted_1 = _convert_obj_to_dict(pill_1)
    converted_2 = _convert_obj_to_dict(pill_2)
    firebasemanager.db.collection("pills").document(pill_1.pillname).set(converted_1)
    firebasemanager.db.collection("pills").document(pill_2.pillname).set(converted_2)
    
    return firebasemanager


def test_get_all_slim_pills(firebasemanager):
    firebasemanager = mock_data(firebasemanager)
    result = firebasemanager.get_all_pills_slim()

    assert len(result) == 4


def test_get_all_extended_pills(firebasemanager):
    firebasemanager = mock_data(firebasemanager)
    result = firebasemanager.get_all_extended_pills()

    assert len(result) == 2


def test_get_specific_pill(firebasemanager):
    firebasemanager = mock_data(firebasemanager)
    result = firebasemanager.get_specific_pill("Viagra")

    assert result['pillname'] == "Viagra"
    assert result['substance'] == "Villigril"
