"""
Logging utility
"""
import sys
import logging


def create_logger(name):
    """
    This function creates a standard logger with specific settings about:
    - stream handler (stdout enabled)
    - logging format
    :param name: the name of the logger
    :type name: str
    :return: the initialized logger object
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
