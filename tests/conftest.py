import os
import uuid
import json

from pytest import fixture

from source.repository import firestore as fs
from source.config import readconfig, CONFIG


@fixture(scope="session")
def firebasemanager():

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

    return fbm
