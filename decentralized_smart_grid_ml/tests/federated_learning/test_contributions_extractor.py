import unittest
from unittest.mock import patch, call

from decentralized_smart_grid_ml.exceptions import NotValidAggregationMethod
from decentralized_smart_grid_ml.federated_learning.contributions_extractor import ContributionsExtractorCreator, \
    ContributionsExtractor, ContributionsExtractorEnsembleGeneral, ContributionsExtractorSimpleAverage


class TestContributionsExtractor(unittest.TestCase):

    def test_factory_method(self):
        contributions_extractor_method = ContributionsExtractorCreator.factory_method(
            "ensemble_general",
            "test_model",
            "x_validation",
            "y_validation"
        )
        self.assertIsInstance(contributions_extractor_method, ContributionsExtractorEnsembleGeneral)
        contributions_extractor_method = ContributionsExtractorCreator.factory_method(
            "simple_average",
            "test_model",
            "x_validation",
            "y_validation"
        )
        self.assertIsInstance(contributions_extractor_method, ContributionsExtractorSimpleAverage)
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

    # test added only for coverage
    def test_compute_contribution(self):
        contributions_extractor = ContributionsExtractor("model", "x_validation", "y_validation")
        contributions_extractor.compute_contribution(None)

    @patch("tensorflow.keras.Sequential")
    def test_compute_contribution_ensemble_general(self, model_mock):
        x_val = [[1, 2], [2, 3]]
        y_val = [0, 1]
        participants_weights = [[1, 2], [3, 4]]
        contributions_extractor = ContributionsExtractorEnsembleGeneral(model_mock, x_val, y_val)
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
            call(x_val, y_val),
            call(x_val, y_val)
        ])

    def test_compute_contribution_simple_average(self):
        x_val = [[1, 2], [2, 3]]
        y_val = [0, 1]
        participants_weights = [[1, 2], [3, 4]]
        contributions_extractor = ContributionsExtractorSimpleAverage(None, x_val, y_val)
        alpha_expected = [0.5, 0.5]
        alpha = contributions_extractor.compute_contribution(participants_weights)
        self.assertListEqual(alpha_expected, alpha)
