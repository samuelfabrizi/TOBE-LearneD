import unittest

import numpy as np

from decentralized_smart_grid_ml.exceptions import NotValidAlphaVectorError, NotValidClientsModelsError
from decentralized_smart_grid_ml.federated_learning.federated_aggregator import weighted_average_aggregation


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