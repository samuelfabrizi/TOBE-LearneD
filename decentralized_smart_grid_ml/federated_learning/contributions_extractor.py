from abc import abstractmethod

from scipy.special import softmax

from decentralized_smart_grid_ml.exceptions import NotValidAggregationMethod
from decentralized_smart_grid_ml.utils.bcai_logging import create_logger

logger = create_logger(__name__)


class ContributionsExtractorCreator:

    @staticmethod
    def factory_method(method, model, x_test, y_test):
        if method is None or method == "ensamble_general":
            # default method
            return ContributionsExtractorEnsambleGeneral(model, x_test, y_test)
        else:
            logger.error("The method '%s' is not valid", method)
            raise NotValidAggregationMethod("The given method is not valid")


class ContributionsExtractor:

    def __init__(self, model, x_test, y_test):
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

    def compute_contribution(self, models_weights):
        evaluation_participants = []
        for model_weight in models_weights:
            self.model.set_weights(model_weight)
            evaluation_participants.append(self.model.evaluate(self.x_test, self.y_test)[1])
        alpha = softmax(evaluation_participants)
        logger.debug("The contribution vector computed is %s", alpha)
        return alpha
