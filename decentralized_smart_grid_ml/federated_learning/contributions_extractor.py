"""
This module contains classes and functions used to compute the participants' contribution
"""
from abc import abstractmethod

from decentralized_smart_grid_ml.exceptions import NotValidAggregationMethod
from decentralized_smart_grid_ml.utils.bcai_logging import create_logger

logger = create_logger(__name__)


class ContributionsExtractorCreator:
    """
    This class contains the factory method used to create a
    ContributionsExtractor
    """

    @staticmethod
    def factory_method(method, model, x_validation, y_validation):
        """
        Creates a ContributionsExtractor instance
        :param method: method used for the contribution extraction
        :param model: global model structure
        :param x_validation: validation features
        :param y_validation: validation labels
        :return: ContributionsExtractor instance
        """
        if method == "ensemble_general":
            # default method
            return ContributionsExtractorEnsembleGeneral(model, x_validation, y_validation)
        elif method == "simple_average":
            return ContributionsExtractorSimpleAverage(model, x_validation, y_validation)
        logger.error("The method '%s' is not valid", method)
        raise NotValidAggregationMethod("The given method is not valid")


class ContributionsExtractor:
    """
    Superclass that represents a ContributionsExtractor
    """

    def __init__(self, model, x_validation, y_validation):
        """
        Initializes the ContributionsExtractor
        :param model: global model structure
        :param x_validation: validation features
        :param y_validation: validation labels
        """
        if x_validation is None or y_validation is None:
            logger.error("The arguments %s are not correct", [model, x_validation, y_validation])
            raise ValueError("The input arguments are not valid")
        self.model = model
        self.x_validation = x_validation
        self.y_validation = y_validation

    @abstractmethod
    def compute_contribution(self, models_weights):
        """
        Computes the participants' contribution
        :param models_weights: participants models' weights (one for each participant in this round)
        :return: vector of the contribution
        """
        pass


class ContributionsExtractorEnsembleGeneral(ContributionsExtractor):
    """
    This class contains the logic to extract the participants' contribution using
    an ensemble model based on the local models' output
    """

    def compute_contribution(self, models_weights):
        evaluation_participants = []
        for model_weight in models_weights:
            self.model.set_weights(model_weight)
            evaluation_participants.append(self.model.evaluate(self.x_validation, self.y_validation)[1])
        logger.debug("Participants models' evaluation: %s", evaluation_participants)
        sum_eval = sum(evaluation_participants)
        alpha = []
        for eval_participant in evaluation_participants:
            if eval_participant == 0.0:
                alpha.append(0)
            else:
                alpha.append(eval_participant / sum_eval)
        # alpha = softmax(evaluation_participants)
        logger.debug("The contribution vector computed is %s", alpha)
        return alpha


class ContributionsExtractorSimpleAverage(ContributionsExtractor):
    """
    This class contains the logic to extract the participants' contribution using
    a simple average of participants models' weights
    """
    def compute_contribution(self, models_weights):
        n_participants = len(models_weights)
        eval_participant = round(1.0 / n_participants, 2)
        alpha = [eval_participant for _ in range(n_participants)]
        logger.debug("The contribution vector computed is %s", alpha)
        return alpha
