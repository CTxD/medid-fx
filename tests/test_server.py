import pytest

from source import server
from source.config import CONFIG, readconfig

if not CONFIG:
    readconfig('config.cfg')


@pytest.fixture(params=['DEV', 'PROD'])
def env_mock(request):
    originalenv = server.CONFIG['ENVIRONMENT']
    server.CONFIG['ENVIRONMENT'] = request.param
    
    yield server.CONFIG['ENVIRONMENT']

    # Revert to original env
    server.CONFIG['ENVIRONMENT'] = originalenv


def test_createadd(env_mock):  
    app = server.createapp()

    assert server.CONFIG['ENVIRONMENT'] == env_mock
    assert app.options.openapi_console_ui_available == (env_mock == 'DEV') # noqa
    

def test_Server(env_mock): # noqa
    serverobj = server.Server(server.createapp())
    bind = f'{server.CONFIG["HOST"]}:{server.CONFIG["PORT"]}'
    assert serverobj.cfg.settings['bind'].value == [bind]


def test_development(env_mock, caplog):
    server.development()

    assert len(caplog.records) == (1 if env_mock == 'PROD' else 0)
    msg = 'Cannot invoke development function in a non-development environment!' if env_mock == 'PROD' else ''
    assert msg in caplog.text 
    
    if env_mock == 'PROD':
        assert caplog.records[0].levelname == 'WARNING'


