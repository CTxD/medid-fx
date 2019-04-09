import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logformat = logging.Formatter(
    '[%(asctime)s] :: [%(levelname)s] :: [%(name)s] >> %(message)s')
ch.setFormatter(logformat)

logger.addHandler(ch)