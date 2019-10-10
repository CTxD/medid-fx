from source.api.v1 import endpoints


def test_get_fsm_uninitialized(firebasemanager):
    # Hard-set the _firestore_repo to None
    endpoints._firestore_repo = None # noqafirebasemanager

    def getfirebasemanagerfixture():
        return firebasemanager

    # Monkeypatch firestore.FBManager() to return the firebasemanager obj
    original = endpoints.firestore.FBManager
    endpoints.firestore.FBManager = getfirebasemanagerfixture
    fbm = endpoints.get_fsm()
    assert isinstance(fbm, original)

    endpoints.firestore.FBManager = original


def test_get_fsm_initialized(firebasemanager):
    endpoints._firestore_repo = firebasemanager # noqa

    assert endpoints.get_fsm() == firebasemanager # noqa


def test_medinfo_slim_success(firebasemanager, monkeypatch):
    endpoints._firestore_repo = firebasemanager # noqa
    
    def allslim():
        return []

    monkeypatch.setattr(firebasemanager, "get_all_pills_slim", allslim)

    assert endpoints.medinfo_slim() == ([], 200)


def test_medinfo_slim_failure(firebasemanager, monkeypatch):
    endpoints._firestore_repo = firebasemanager # noqa
    
    def allslim():
        raise Exception('Some message')

    monkeypatch.setattr(firebasemanager, "get_all_pills_slim", allslim)

    # original = firebasemanager.get_all_pills_slim
    # firebasemanager.get_all_pills_slim = lambda: raise Exception('Some message')
    errorschema, statuscode = endpoints.medinfo_slim()
    
    assert errorschema.message == 'Some message'
    assert statuscode == 500