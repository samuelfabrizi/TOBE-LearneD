import unittest
from unittest.mock import patch, call

from decentralized_smart_grid_ml.exceptions import NotValidAggregationMethod
from decentralized_smart_grid_ml.federated_learning.contributions_extractor import ContributionsExtractorCreator, \
    ContributionsExtractor, ContributionsExtractorEnsembleGeneral


class TestContributionsExtractor(unittest.TestCase):

    def test_factory_method_not_valid_method(self):
        with self.assertRaises(NotValidAggregationMethod):
            ContributionsExtractorCreator.factory_method(
                "not_existing_method",
                "test_model",
                "x_validation",
                "y_validation"
            )

    def test_contributions_extractor_creation_not_valid_arguments(self):
        with self.assertRaises(ValueError):
            ContributionsExtractor(None, None, None)

    def test_compute_contribution(self):
        # test added only for coverage
        contributions_extractor = ContributionsExtractor("model", "x_validation", "y_validation")
        contributions_extractor.compute_contribution(None)

    #@patch('decentralized_smart_grid_ml.federated_learning.contributions_extractor.softmax')
    @patch("tensorflow.keras.Sequential")
    def test_compute_contribution_ensemble_general(self, model_mock,
                                                   #softmax_mock
                                                   ):
        x_test = [[1, 2], [2, 3]]
        y_test = [0, 1]
        participants_weights = [[1, 2], [3, 4]]
        #softmax_mock.return_value = [0.5, 0.5]
        contributions_extractor = ContributionsExtractorEnsembleGeneral(model_mock, x_test, y_test)
        models_evaluation = [1.0, 0.0]
        model_mock.evaluate.side_effect = [
            ["loss0", models_evaluation[0]],
            ["loss1", models_evaluation[1]],
        ]
        contributions_extractor.compute_contribution(participants_weights)
        model_mock.set_weights.assert_has_calls([
            call(participants_weights[0]),
            call(participants_weights[1])
        ])
        model_mock.evaluate.assert_has_calls([
            call(x_test, y_test),
            call(x_test, y_test)
        ])
        #softmax_mock.assert_called_with(models_evaluation)
