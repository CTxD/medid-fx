import subprocess
import os

from sys import executable, argv
from typing import List, Dict

from source.config import readconfig, CONFIG


def getrequirements(filepath: str) -> List[str]:
    requirements: List[str] = []
    
    with open(filepath) as fp:
        for line in fp.readlines():
            line = line.strip()
            if not line or line[0] == '#':
                continue

            if line.startswith('-r'):
                dependency = line.split()[1]
                requirements.extend(
                    getrequirements(os.path.join(os.path.dirname(filepath), dependency))
                )
                continue
            
            requirements.append(line)
    return requirements


def getuninstalledrequirements(filepath: str) -> List[str]:
    result: List[str] = []
    installedpackages = getinstalledpackages()
    for requirement in getrequirements(filepath):
        if requirement.lower().split('[')[0] not in installedpackages:
            result.append(requirement)
    return result


def getinstalledpackages() -> Dict[str, str]:
    return {
        s.decode('utf-8').split('==')[0].lower(): s.decode('utf-8').split('==')[1] 
        for s in subprocess.check_output([executable, '-m', 'pip', 'freeze']).split()
    }


def install(requirements: List[str] = None):
    # If we run install.py directly, we have to populate the CONFIG dict.
    if not CONFIG:
        readconfig('config.cfg')

    if requirements is None:
        # Check if dependencies are installed according to the ENVIRONMENT defined in the config.cfg
        requirements = getuninstalledrequirements(CONFIG['REQPATH'])
    
    if not requirements:
        print('All requirements are already installed.')
        exit()
    
    try:
        subprocess.check_call([executable, '-m', 'pip', 'install', '-r', CONFIG['REQPATH']])
    except Exception as e:
        print(e)


if __name__ == '__main__':
    install()