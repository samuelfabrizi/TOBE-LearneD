import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from decentralized_smart_grid_ml.exceptions import NotValidAlphaVectorError, NotValidClientsModelsError
from decentralized_smart_grid_ml.federated_learning.federated_aggregator import weighted_average_aggregation, Aggregator


class TestFederatedAggregator(unittest.TestCase):

    def test_weighted_average_aggregation_error_alpha(self):
        # sum(alpha) = 1.1, error
        alpha = [0.1, 0.2, 0.8]
        with self.assertRaises(NotValidAlphaVectorError):
            weighted_average_aggregation([], alpha)

    def test_weighted_average_aggregation_error_clients_number(self):
        # sum(alpha) = 1, ok
        alpha = [0.1, 0.2, 0.7]
        # empty list for the sake of simplicity
        list_weights = [[], [], [], []]
        with self.assertRaises(NotValidClientsModelsError):
            weighted_average_aggregation(list_weights, alpha)

    def test_weighted_average_aggregation(self):
        # sum(alpha) = 1, ok
        alpha = [0.5, 0.5]
        w1 = [
            np.array([1, 2, 3]),
            np.array([4, 5]),
        ]
        w2 = [
            np.array([3, 4, 5]),
            np.array([6, 7]),
        ]
        expected_aggregated_weights = [
            np.array([2, 3, 4]),
            np.array([5, 6])
        ]
        aggregated_weights = weighted_average_aggregation([w1, w2], alpha)
        for expected_layer_weights, layer_weights in zip(expected_aggregated_weights, aggregated_weights):
            np.testing.assert_array_equal(expected_layer_weights, layer_weights)

    def test_weighted_average_aggregation_different_shapes(self):
        # sum(alpha) = 1, ok
        alpha = [0.5, 0.5]
        w1 = [
            np.array([1, 2, 3]),
            np.array([4, 5]),
        ]
        w2 = [
            np.array([3, 4]),    # different shape w.r.t w1[0]
            np.array([6, 7]),
        ]
        with self.assertRaises(NotValidClientsModelsError):
            weighted_average_aggregation([w1, w2], alpha)

    @patch("pandas.read_csv")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.load_fl_model")
    def test_aggregator_constructor(self, load_fl_model_mock, read_csv_mock):
        client_ids = [0, 1, 2]
        n_fl_rounds = 2
        global_model_path = "/path/to/model"
        test_set_path = "/path/to/test.csv"
        read_csv_mock.return_value = pd.DataFrame({
            "x1": [0, 1],
            "x2": [1, 2],
            "y": [0, 1]
        })
        model_artifact = "expected model"
        load_fl_model_mock.return_value = model_artifact
        rounds2participants_expected = {
            0: {
                "participant_weights": [],
                "client_ids": client_ids
            },
            1: {
                "participant_weights": [],
                "client_ids": client_ids
            }
        }
        aggregator = Aggregator(
            client_ids,
            n_fl_rounds,
            global_model_path,
            test_set_path
        )
        read_csv_mock.assert_called_with(test_set_path)
        load_fl_model_mock.assert_called_with(global_model_path)
        self.assertDictEqual(rounds2participants_expected, aggregator.rounds2participants)
        self.assertDictEqual(rounds2participants_expected, aggregator.rounds2participants)
