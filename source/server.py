import os
import logging
import base64

import connexion
from gunicorn.app.base import BaseApplication

from .config import CONFIG
from .fx.colorx import cx
from .fx import fx

logger = logging.getLogger(__name__)


class Server(BaseApplication):
    def __init__(self, app):
        self.application = app
        super().__init__()

    def load_config(self):
        # See https://github.com/benoitc/gunicorn/blob/master/examples/example_config.py for 
        # example config file key/values
        gunicornconfig = {
            'bind': f'{CONFIG["HOST"]}:{CONFIG["PORT"]}'
        }
        
        for key, value in gunicornconfig.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application # pragma: no cover


def createapp():
    options = {
        'swagger_ui': CONFIG['ENVIRONMENT'] == 'DEV' # Only provide the Swagger UI when in DEV env.
    }

    app = connexion.App(__name__, specification_dir=os.getcwd(), options=options)

    # Read the configuration file to configure the endpoints
    app.add_api('apiconfiguration.yaml')

    return app


def development():
    """
    Used while implementing features.

    Allows normal execution of functions WITHOUT STARTING THE SERVER!
    """
    if not CONFIG['ENVIRONMENT'] == 'DEV':
        logger.warning('Cannot invoke development function in a non-development environment!')
        return

    # ## DEVELOPMENT CODE GOES HERE ## #
    # Example:
    # fx.extractfeatures()
    with open('resources/fluox_right.jpg', mode='rb') as f:
        enc = base64.b64encode(f.read())
        fx.m(enc, 'fluox')
    # ## END OF DEVELOPMENT CODE ## #

