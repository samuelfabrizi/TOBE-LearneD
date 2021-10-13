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
        baseline_model_weights_path = "/path/to/new_model_weights"
        read_csv_mock.return_value = pd.DataFrame({
            "x1": [0, 1],
            "x2": [1, 2],
            "y": [0, 1]
        })
        model_artifact = "expected model"
        load_fl_model_mock.return_value = model_artifact
        rounds2participants_expected = {
            0: {
                "valid_participant_ids": client_ids,
                "participant_weights": [],
                "participant_ids": []
            },
            1: {
                "valid_participant_ids": client_ids,
                "participant_weights": [],
                "participant_ids": []
            }
        }
        aggregator = Aggregator(
            client_ids,
            n_fl_rounds,
            global_model_path,
            test_set_path,
            baseline_model_weights_path
        )
        read_csv_mock.assert_called_with(test_set_path)
        load_fl_model_mock.assert_called_with(global_model_path)
        self.assertDictEqual(rounds2participants_expected, aggregator.rounds2participants)
        self.assertDictEqual(rounds2participants_expected, aggregator.rounds2participants)

    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.load_fl_model_weights")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.Aggregator.__init__", return_value=None)
    def test_add_participant_weights(self, aggregator_init_mock, load_fl_model_weights_mock):
        # simulate correct file path for client 0, round 0
        path_file_created = "/clients/client_0/weights_round_0.json"
        load_fl_model_weights_mock.return_value = [1, 2]
        aggregator = Aggregator()
        aggregator.current_round = 0
        aggregator.rounds2participants = {
            0: {
                "valid_participant_ids": [0],
                "participant_weights": [],
                "participant_ids": []
            }
        }
        rounds2participants_expected = {
            0: {
                "valid_participant_ids": [0],
                "participant_weights": [[1, 2]],
                "participant_ids": [0]
            }
        }
        is_completed = aggregator.add_participant_weights(path_file_created)
        load_fl_model_weights_mock.called_with(path_file_created)
        self.assertDictEqual(rounds2participants_expected, aggregator.rounds2participants)
        self.assertEqual(True, is_completed)

    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.Aggregator.__init__", return_value=None)
    def test_add_participant_weights_wrong_round(self, aggregator_init_mock):
        # simulate wrong file path for not existing round 1
        path_file_created = "/clients/client_0/weights_round_1.json"
        aggregator = Aggregator()
        aggregator.current_round = 0
        is_completed = aggregator.add_participant_weights(path_file_created)
        self.assertEqual(False, is_completed)

    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.load_fl_model_weights")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.Aggregator.__init__", return_value=None)
    def test_add_participant_weights_wrong_client_id(self, aggregator_init_mock, load_fl_model_weights_mock):
        # simulate wrong file path for not existing client 1
        path_file_created = "/clients/client_1/weights_round_0.json"
        aggregator = Aggregator()
        aggregator.current_round = 0
        aggregator.rounds2participants = {
            0: {
                # the client id 1 is not present in the valid ones
                "valid_participant_ids": [0],
                "participant_weights": [],
                "participant_ids": []
            }
        }
        is_completed = aggregator.add_participant_weights(path_file_created)
        self.assertEqual(False, is_completed)

    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.weighted_average_aggregation")
    @patch("tensorflow.keras.Sequential")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.save_fl_model_weights")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.Aggregator.__init__", return_value=None)
    def test_update_global_model(self, aggregator_init_mock, save_fl_model_weights_mock,
                                 global_model_mock, weighted_average_aggregation_mock):
        baseline_model_weights_path = "/path/to/new_model_weights/"
        evaluation = ["0.8", "0.7"]
        x_test = [[1, 2], [2, 3]]
        y_test = [0, 1]
        global_model_mock.evaluate.return_value = evaluation
        global_weights = [2, 3]
        weighted_average_aggregation_mock.return_value = global_weights
        aggregator = Aggregator()
        aggregator.current_round = 0
        aggregator.x_test = x_test
        aggregator.y_test = y_test
        aggregator.baseline_model_weights_path = baseline_model_weights_path
        aggregator.rounds2participants = {
            0: {
                "valid_participant_ids": [0, 1],
                "participant_weights": [[1, 2], [3, 4]],
                "participant_ids": [0, 1]
            }
        }
        aggregator.global_model = global_model_mock
        rounds2participants_expected = {
            0: {
                "valid_participant_ids": [0, 1],
                "participant_weights": [[1, 2], [3, 4]],
                "participant_ids": [0, 1],
                "alpha": [0.5, 0.5],
                "evaluation": evaluation
            }
        }
        aggregator.update_global_model()
        global_model_mock.set_weights.assert_called_with(global_weights)
        global_model_mock.evaluate.assert_called_with(
            x_test,
            y_test
        )
        save_fl_model_weights_mock.assert_called_with(
            global_model_mock,
            baseline_model_weights_path + "validator_weights_round_0.json",
        )
        self.assertDictEqual(
            rounds2participants_expected,
            aggregator.rounds2participants
        )
        self.assertEqual(1, aggregator.current_round)


