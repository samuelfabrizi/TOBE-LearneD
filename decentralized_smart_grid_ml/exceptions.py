"""
This module defines all the exceptions for Decentralized-SmartGrid-ML
"""


class DecentralizedSmartGridML(Exception):
    """ This is the base class of DecentralizedSmartGridML errors """


class IncorrectExtensionFileError(DecentralizedSmartGridML):
    """ This exception arises when a file path has an incorrect extension """
