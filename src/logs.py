import logging
import os

path = "/".join(os.path.dirname(os.path.realpath(__file__)).split("/")[0:-1])
DEBUG_LOG = path + "/data/debugs.log"
ERROR_LOG = path + "/data/errors.log"


def get_logger():
    logger = logging.getLogger('debugs')
    logger.setLevel(logging.DEBUG)
    if len(logger.handlers) == 0:
        debugHandler = logging.FileHandler(DEBUG_LOG)
        errorHandler = logging.FileHandler(ERROR_LOG)
        formatter = logging.Formatter('%(asctime)s|%(levelname)7s|%(filename)20s (%(lineno)04d)|\t%(message)s')
        debugHandler.setFormatter(formatter)
        errorHandler.setFormatter(formatter)
        errorHandler.setLevel(logging.ERROR)
        logger.addHandler(debugHandler)
        logger.addHandler(errorHandler)
    return logger