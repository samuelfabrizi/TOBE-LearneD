"""
This module contains classes and functions used to compute the participants' contribution
"""
from abc import abstractmethod

from scipy.special import softmax

from decentralized_smart_grid_ml.exceptions import NotValidAggregationMethod
from decentralized_smart_grid_ml.utils.bcai_logging import create_logger

logger = create_logger(__name__)


class ContributionsExtractorCreator:
    """
    This class contains the factory method used to create a
    ContributionsExtractor
    """

    @staticmethod
    def factory_method(method, model, x_test, y_test):
        """
        Creates a ContributionsExtractor instance
        :param method: method used for the contribution extraction
        :param model: global model structure
        :param x_test: test features
        :param y_test: test labels
        :return: ContributionsExtracto instance
        """
        if method is None or method == "ensamble_general":
            # default method
            return ContributionsExtractorEnsambleGeneral(model, x_test, y_test)
        logger.error("The method '%s' is not valid", method)
        raise NotValidAggregationMethod("The given method is not valid")


class ContributionsExtractor:
    """
    Superclass that represents a ContributionsExtractor
    """

    def __init__(self, model, x_test, y_test):
        """
        Initializes the ContributionsExtractor
        :param model: global model structure
        :param x_test: test features
        :param y_test: test labels
        """
        if model is None or x_test is None or y_test is None:
            logger.error("The arguments %s are not correct", [model, x_test, y_test])
            raise ValueError("The input arguments are not valid")
        self.model = model
        self.x_test = x_test
        self.y_test = y_test

    @abstractmethod
    def compute_contribution(self, models_weights):
        """
        Computes the participants' contribution
        :param models_weights: participants models' weights (one for each participant in this round)
        :return: vector of the contribution
        """
        pass


class ContributionsExtractorEnsambleGeneral(ContributionsExtractor):
    """
    This class contains the logic to extract the participants' contribution using
    an ensamble model based on the local models' output
    """
    def compute_contribution(self, models_weights):
        evaluation_participants = []
        for model_weight in models_weights:
            self.model.set_weights(model_weight)
            evaluation_participants.append(self.model.evaluate(self.x_test, self.y_test)[1])
        alpha = softmax(evaluation_participants)
        logger.debug("The contribution vector computed is %s", alpha)
        return alpha
