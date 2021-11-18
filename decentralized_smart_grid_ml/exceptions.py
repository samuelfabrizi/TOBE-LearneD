"""
This module defines the exceptions for Decentralized SmartGrid ML
"""


class DecentralizedSmartGridML(Exception):
    """ This is the base class of DecentralizedSmartGridML errors """


class IncorrectExtensionFileError(DecentralizedSmartGridML):
    """ This exception arises when a file path has an incorrect extension """


class NotValidParticipantsModelsError(DecentralizedSmartGridML):
    """ This exception arises when the clients' models do not correspond
    with what is required """


class NotValidAlphaVectorError(DecentralizedSmartGridML):
    """ This exception arises when the vector of the weights (alpha) is not valid """


class NotValidAggregationMethod(DecentralizedSmartGridML):
    """ This exception arises when the aggregation method is not valid """
