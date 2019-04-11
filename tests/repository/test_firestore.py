# pylint:disable=protected-access
import os
import uuid
import json

import mockfirestore

import source.repository.firestore as fs
from source.config import CONFIG, readconfig
from source.models.v1 import pill

if not CONFIG:
    readconfig('config.cfg')

tmppath = os.path.join(os.getcwd(), str(uuid.uuid4()))
filepath = os.path.join(tmppath, str(uuid.uuid4()))

certificate = {
    "type": "service_account",
    "project_id": "private",
    "private_key_id": "private",
    # NOTICE: private_key is just a randomly generated 2048 bit RSA-256 key! Don't worry.
    "private_key": """
-----BEGIN RSA PRIVATE KEY----- 
MIIEowIBAAKCAQEA03wWZwzGc03ECCvGcRd9xcKT7hhofsYmun2jmsod2HRFQvoJ
XFFJbIV8ExSAIBM8Hb7lYGd/wTEM5WLAOCD/J/VSekgoWsEkgMCuXO1Y85sifDTW
7oqVTfguaEvVNqjiK9EVZrk2cLRvFaxy+vC4+cp904Y90POGZV9GAuSUSaVsptof
pD03diCfzdN7WvbaCFoMpGHAuVzt+9e2gmj/gQr5HEh487yfqbFiEap7xbjjrtEe
reYDHtJHzKPoXOaJ/n/g8zz0zAS7awPc0mjdNCBh7Og1uSJStnLD3MMm35eV8CPO
bHQKOX+QNgcotVVPcvYeDgHwRK5H3PjVnUUafwIDAQABAoIBAFxOlASkmdXoAoFC
ghoIk9gGhsTsmGeFG5BYmFlOkNpSXYzPT9igjji0xqQZVZcqbhnZoYqDgkqTmzpf
8OBO3q/VLwu6hQqftMwRzck3u5SQiOvHsGxrxqFCixbwyn5SFm3jk8DDZJSq3LWM
EJ+hBEva6zKxLDgQov+KJyfKF0NRCnJ3TqaS4/7wFpNHxAHNu5V99kMPj5Sp9tLM
Q95ijEKFM92AfESkPgIIf7gvgTtMUM5yE4hmFxLqM3duU3WW5YIJ8aUfBDYxbvkx
kzV7J1WLI+agATIkQ65ul0IBypYWQDZyFrt4u+RNDDMKU5/UybrEJIvwLHHaTz0x
ZMarHQECgYEA9uW/Z6OYt/heyxbhjVenKt9dcNsScTwnzvjP+etDiG95uyeYbHoz
v2Ih0DRHwy/Rdg/UQiUtQEFVOj1ZaW9kyWG2gaBS18sAp/n8S7Fk9MMuFYbge2gA
I1LUrYE68TYOg/7W5cVZJmG4ecrSzFD0fQTr1hfh7gb4DHImJZY9qf8CgYEA20gc
CtAq1WhnJnAiN/UaEHvWELhaJICxY6pbodNdG3O/fU/VxdptGZuC6tx9GbK7/tQc
6OXjpJSAw3qsWbdwmGl1D+WJdLUAjquZWbRNeXGGIYhaMKC3mSy8onu0fIHomB2v
6lSKuDIouNMDi2JqIiWaq1X1Z+FPhJ6bpgfDj4ECgYBGmlqK05CXg1HwN6HWXmty
ah95Z1w1v2MO373xlOJiAKbJ6z++PY/Quco7lMe0vFbksRAcvi7bghNSLTsFWJJ0
uBmNpgAqr2WHo4gPSTI6gBoMk95by9jGQSiKWTs2wSOTgWuIl0+wFx++zE5NmRTh
L2gVeAzmmV2TiYz5EKaflwKBgEPP0fQ6GfTzG2sUpFBfuNa+JR34lM/TCIiEx1+N
CK8TpXUwOjC8cp7Hq73Lv9gxoNeWavZPGY3s6sEI78Gy69wGSNBIsLBpxSlZwcuu
6YKT6+H008dT/FMfNZqd3NvgJLjd/WffCyMZR+SYRPFW1vGGZYV0yLZ+Q+QEVKgM
oJqBAoGBAN0I9+DNsSJuHfwYn0UMruq7VVCNwDzJEb99GDFaI97Vicn/X5aeOjnX
zY9DlKS+gBCtcQbbxS42nenA5G2MdEQPiKTUlqAz5zeU3liOZ8xHHd9yoQNz2HlR
wAiifqWPbKZzOAvTpdojatv5us0N3t038mQxxmb94tVbAJkBxDb1
-----END RSA PRIVATE KEY-----""",
    "client_email": "my@email.com",
    "client_id": "1234",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://google.com"
}

# Setup of mocking certificate file
# Create the path and file and write the certificate into the file.
if not os.path.exists(tmppath):
    os.mkdir(tmppath)
with open(filepath, 'w') as fp:
    json.dump(certificate, fp, indent=4)

# Point to the mocked certificate file
oldpath = CONFIG['CERT']
CONFIG['CERT'] = filepath

# Create our FBManager instance to be used during testing
fbm = fs.FBManager()

# Revert the mocked certificate file point
CONFIG['CERT'] = oldpath

# Teardown of mocking certificate file
# Delete the mock file
os.remove(filepath)

# Delete temp folder, if it is empty
if not os.listdir(tmppath):
    os.rmdir(tmppath)

# Grab the db instance of fbm and monkey-patch it to a mocked one instead.
fbm.db = mockfirestore.MockFirestore()


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


def mock_data():
    fbm.db.reset()

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
    fbm.db.collection("pills").document(pill_1.pillname).set(converted_1)
    fbm.db.collection("pills").document(pill_2.pillname).set(converted_2)


def test_get_all_slim_pills():
    mock_data()
    result = fbm.get_all_pills_slim()

    assert len(result) == 4


def test_get_all_extended_pills():
    mock_data()
    result = fbm.get_all_extended_pills()

    assert len(result) == 2


def test_get_specific_pill():
    mock_data()
    result = fbm.get_specific_pill("Viagra")

    assert result['pillname'] == "Viagra"
    assert result['substance'] == "Villigril"
