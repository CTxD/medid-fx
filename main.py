import logging
import os
import sys

from typing import Union

from source import config, server
from install import getuninstalledrequirements, install


# The logger is configured in source/__init__.py, so make sure to import something from source 
# before getting a logger instance. This way we use that configuration instead of creating a new,
# default configuration. Also, the name of the logger must be 'source' (instead of __name__) when
# getting a logger instance here, as it will manipulate the logger to believe this file is part of
# the source module (which it is not!). In all other places __name__ should still be used when
# getting logger instances!
logger = logging.getLogger('source')


def main():
    if '-I' in sys.argv:
        install()

    if not resolvedependencies():
        exit()
    print('Everything OK!\r\n')


def checkrequirements() -> bool:
    # Are all requirements installed?
    printstatus('Checking requirements')
    res = getuninstalledrequirements(config.CONFIG['REQPATH'])

    status = False if res else True
    printstatus(status)

    if not status:
        print(f'\r\nThe following package{"s" if len(res) > 1 else ""} needs to be installed:')
        for req in res:
            print(' - ' + req)
        print(
            '\r\nRun one of the following commands to resolve dependencies:\r\n'
            f'\tmake isntall\r\n'
            f'\tpip install -r {config.CONFIG["REQPATH"]}\r\n'
            f'\tpython main.py -I'
        )

    return status


def checkconnection() -> bool:
    # Access to DB instance?
    printstatus('Connection to DB instance')
    status = True
    printstatus(status)

    return status


def checkconfig() -> bool:
    printstatus('Checking config file')
    status = True
    extra = ''

    # Does a file named config.cfg exist?
    if not os.path.exists(os.path.join(os.getcwd(), 'config.cfg')):
        status = False
        extra = '\r\nNo config.cfg file exists or it is misplaced. Make sure the config.cfg file '\
                f'is located in the {os.getcwd()} directory.'
        # If a config.cfg.example file exists, inform the user to use that.
        if os.path.exists(os.path.join(os.getcwd(), 'config.cfg.example')):
            extra = extra + '\r\nA template config.cfg file exists. Make a copy of ' \
                'config.cfg.example template file, renaming it config.cfg.'
            
    printstatus(status)
    
    if extra:
        print(extra)

    return status
 

def resolvedependencies() -> bool:
    if not checkconfig():
        return False

    config.readconfig('config.cfg')

    if not checkrequirements() or not checkconnection():
        return False
    
    return True


def printstatus(status: Union[str, bool]):
    message = ''
    if isinstance(status, str):
        message = "{:<40}".format(status+'...')
    else:
        message = "\033[92m OK!\033[00m" if status is True else "\033[91m Failed\033[00m"
        message = message + '\r\n'

    sys.stdout.write(message)
    sys.stdout.flush()


if __name__ == '__main__':
    main()  
    logger.info('Starting application.')

    if '--dev' in sys.argv:
        logger.info('Note: Using -dev flag will execute code in server.development, but will NOT start the server!') # noqa
        server.development()
    else:
        server.Server(server.createapp()).run()