import logging
import re
import os
import warnings

from configparser import ConfigParser
from typing import Union, List, Any


logger = logging.getLogger(__name__)


class CONFIGDICT(dict):
    """This is a config dict wrapper"""
    pass
        

CONFIG: CONFIGDICT = CONFIGDICT()


def readconfig(filepath: str) -> None:
    # Make sure we don't accidentally read configruations multiple times
    if CONFIG:
        return

    if not os.path.exists(filepath):
        raise FileNotFoundError(f'No config file exists with the name/path {filepath}.') 

    cfg = ConfigParser()
    # Changing the optionxform enables case preservation of keys in configurations.
    cfg.optionxform = lambda option: option # type: ignore

    cfg.read(filepath)

    # Store TEMPLATE key/value pairs outside the CONFIG dict
    envspecifics: CONFIGDICT = CONFIGDICT()

    # Sections in the config file are flattened, so all configurations are placed on the same level
    for section in cfg:
        storedict = envspecifics if section == 'ENVIRONMENTSPECIFIC' else CONFIG
            
        for key, value in cfg[section].items():
            storedict[key] = simplevalueparser(value)

    # Manually set values from the ENVIRONMENTSPECIFIC section based on the ENVIRONMENT variable.
    for envkey, value in envspecifics.items():
        try:
            env = envkey.split('_')[0]
            key = envkey.split('_')[1]
        except Exception:
            warnings.warn(
                f'Key {envkey} is not a valid ENVIRONMENTSPECIFIC key.'
            )
            continue

        if env not in ('DEV', 'PROD'):
            warnings.warn(
                f'Environment specifier {env} is not a valid environment.'
                'Valid options are DEV and PROD.'
            )
            continue
        
        # Skip all variables which are not for the current ENVIRONMENT
        if env != CONFIG['ENVIRONMENT']:
            continue
        
        if key in CONFIG:
            warnings.warn(
                f'Key {key} is already specified with value {CONFIG[key]}. '
                f'Overwriting the value for the environment-specific value {value}.'
            )

        # Set the key/value pair
        CONFIG[key] = value


def simplevalueparser(value: str) -> Union[str, bool, int, float, List[Any]]: 
    # Case: Bools
    if value.lower() in ['true', 'false']:
        return value.lower() == 'true'
    
    # Case: Numbers
    # Match any number, which can be represented as <1> and <1.0>
    digitre = r'-?\d+([.]\d+)?'

    rematch = re.match(digitre, value)
    # Determine if the value is a number. Second check is to filter out IP adresses, for which
    # the RE also (partially) matches.
    if rematch and rematch.span(0)[1] == len(value):
        return int(value) if rematch.group(1) is None else float(value)

    # Case: List
    # Base case for lists:
    if value == '[]':
        return []

    if len(value) > 2 and value[0] == '[' and value[-1] == ']':
        result: list = []
        # All values are themselves cast to their respective types by the simplevalueparser
        for listvalue in value[1:-1].split(','):
            result.append(simplevalueparser(listvalue.strip()))

        return result

    # Base case: Return the un-altered string as value
    return value