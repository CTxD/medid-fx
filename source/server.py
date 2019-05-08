import os
import logging
import base64

import connexion
from gunicorn.app.base import BaseApplication
import cv2 as cv

from .config import CONFIG
from .fx import fx
from .fx.utils import encoding2img, showimg
from .fx.shapex import ShapePreprocessor


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

    pillname = 'fexo.jpg'

    with open(f'resources/{pillname}', mode='rb') as f:
        fx.m(base64.b64encode(f.read()), pillname.split('.')[0])
    return

    def splitproimg(imgpath):
        with open(imgpath, mode='rb') as f:
            with encoding2img.Encoding2IMG(base64.b64encode(f.read())) as tmpimgpath:
                left, right = ShapePreprocessor().crop_image(tmpimgpath, grayscale=False)
                tmpimgname, tmpimgext = os.path.basename(tmpimgpath).split('.')
                tmpimgpath = os.path.dirname(tmpimgpath)
                leftimgpath = os.path.join(tmpimgpath, f'{tmpimgname}_left.{tmpimgext}')
                rightimgpath = os.path.join(tmpimgpath, f'{tmpimgname}_right.{tmpimgext}')
                cv.imwrite(leftimgpath, cv.cvtColor(left, cv.COLOR_RGB2BGRA))
                cv.imwrite(rightimgpath, cv.cvtColor(right, cv.COLOR_RGB2BGRA))
                yield leftimgpath
                yield rightimgpath

    sp = ShapePreprocessor()

    for tmpimgpath in splitproimg(f'resources/{pillname}'):
        img = cv.cvtColor(cv.imread(tmpimgpath, 0), cv.COLOR_RGB2BGR)
        showimg.showimgs(['split', 'contours'], [img, showimg.get_contour_drawing(*sp.get_contours(img))])
        with open(tmpimgpath, mode='rb') as f:
            enc = base64.b64encode(f.read())
            fx.m(enc, f'{pillname.split(".")[0]}_{tmpimgpath.split("_")[1].split(".")[0]}')
    # # ## END OF DEVELOPMENT CODE ## #


    # Encoding af pro.medicin.dk billede som input:
    # -> temp billede
    # -> Croppes til 2 billeder (numpy arrays)
    # -> Gemmes til 2 seperate billeder (<imgname>_left og <imgname>_right e.g.)
    # -> Repeat proces for begge billeder.

