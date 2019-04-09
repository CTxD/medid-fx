import os
import uuid
from configparser import DuplicateOptionError, DuplicateSectionError

import pytest

from source.config import config


@pytest.mark.parametrize("test_input, expected", [
    # Bool values
    ('True', True),
    ('trUe', True),
    ('FALSE', False),
    ('false', False),

    # Number values
    ('1', 1),
    ('123', 123),
    ('-1', -1),
    ('12.34', 12.34),

    # List values
    ('[1, true, string]', [1, True, "string"]),
    ('[]', []),
    ('[1]', [1]),

    # String values
    ("string", "string"),
    ("string with multiple words", "string with multiple words"),
    ("", "") # Empty string
])
def test_simplevalueparser(test_input, expected):
    assert config.simplevalueparser(test_input) == expected


# Helper-class to create a temporary mock config-file and delete it afterwards
class TempConfigMock():
    def __init__(self, body: str):
        self.body = body
        self.tmppath = os.path.join(os.getcwd(), str(uuid.uuid4()))
        self.filepath = os.path.join(self.tmppath, str(uuid.uuid4()))

    def __enter__(self):
        if not os.path.exists(self.tmppath):
            os.mkdir(self.tmppath)
        with open(self.filepath, 'w') as fp:
            fp.write(self.body)

        return self.filepath

    def __exit__(self, ttype, value, traceback):
        # Delete file
        os.remove(self.filepath)

        # Delete temp folder, if it is empty
        if not os.listdir(self.tmppath):
            os.rmdir(self.tmppath)


def resetconfig():
    config.CONFIG = config.CONFIGDICT()   


def test_readconfig_no_config_file():
    resetconfig()
    with pytest.raises(FileNotFoundError):
        config.readconfig('no file with this name exists')
        

def test_readconfig_duplicate_values():
    configbody = """
[SECTION]
KEY1 = Value1
KEY1 = Value2
    """
    resetconfig()

    with TempConfigMock(configbody) as mock:
        with pytest.raises(DuplicateOptionError):
            config.readconfig(mock)


def test_readconfig_duplicate_sections():
    configbody = """
[SECTION]
KEY1 = Value1

[SECTION]
KEY2 = Value2
    """
    resetconfig()

    with TempConfigMock(configbody) as mock:
        with pytest.raises(DuplicateSectionError):
            config.readconfig(mock)


def test_readconfig_valid_config():
    configbody = """
[SECTION1]
KEY1 = Value1

[SECTION2]
KEY2 = Value2
    """
    resetconfig()

    with TempConfigMock(configbody) as mock:
        config.readconfig(mock)

        assert "KEY1" in config.CONFIG
        assert config.CONFIG["KEY1"] == "Value1"

        assert "KEY2" in config.CONFIG
        assert config.CONFIG["KEY2"] == "Value2"


def test_readconfig_valid_environmentspecific_key():
    configbody = """
[SECTION1]
ENVIRONMENT = DEV

[ENVIRONMENTSPECIFIC]
DEV_KEY = Value
    """
    resetconfig()

    with TempConfigMock(configbody) as mock:
        config.readconfig(mock)

        assert "KEY" in config.CONFIG
        assert config.CONFIG["KEY"] == "Value"


def test_readconfig_invalid_environmentspecific_key():
    configbody = """
[SECTION1]
ENVIRONMENT = DEV

[ENVIRONMENTSPECIFIC]
DEVKEY = Value
    """
    resetconfig()

    with TempConfigMock(configbody) as mock:
        with pytest.warns(UserWarning, match=r'not a valid ENVIRONMENTSPECIFIC key'):
            config.readconfig(mock)


def test_readconfig_invalid_environment_specifier():
    configbody = """
[SECTION1]
ENVIRONMENT = DEV

[ENVIRONMENTSPECIFIC]
INVALID_KEY = Value
    """
    resetconfig()

    with TempConfigMock(configbody) as mock:
        with pytest.warns(UserWarning, match=r'not a valid environment.'):
            config.readconfig(mock)


def test_readconfig_environmentspecific_variable_for_other_environment():
    configbody = """
[SECTION1]
ENVIRONMENT = DEV

[ENVIRONMENTSPECIFIC]
PROD_KEY = Value
    """
    resetconfig()

    with TempConfigMock(configbody) as mock:
        config.readconfig(mock)

        assert "KEY" not in config.CONFIG


def test_readconfig_overwriting_value_with_environmenspecific_value():
    configbody = """
[SECTION1]
ENVIRONMENT = DEV

[SECTION2]
KEY = OldValue

[ENVIRONMENTSPECIFIC]
DEV_KEY = NewValue
    """
    resetconfig()

    with TempConfigMock(configbody) as mock:
        with pytest.warns(UserWarning, match=r'Overwriting the value for the environment-specific'):
            config.readconfig(mock)

        assert "KEY" in config.CONFIG
        assert config.CONFIG["KEY"] == "NewValue"



def test_readconfig_multiple_config_read_guard():
    configbody1 = """
[SECTION1]
Key = Value1
    """ 
    configbody2 = """
[SECTION1]
Key = Value2
    """ 
    resetconfig()
    with TempConfigMock(configbody1) as mock:
        config.readconfig(mock)
    with TempConfigMock(configbody2) as mock:
        config.readconfig(mock)
    
    assert config.CONFIG['Key'] == 'Value1'

