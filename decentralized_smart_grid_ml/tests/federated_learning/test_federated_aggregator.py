import pathlib
import unittest
from unittest.mock import patch, call, mock_open

import numpy as np
import pandas as pd

from decentralized_smart_grid_ml.exceptions import NotValidAlphaVectorError, NotValidParticipantsModelsError
from decentralized_smart_grid_ml.federated_learning.federated_aggregator import weighted_average_aggregation, Aggregator


class TestFederatedAggregator(unittest.TestCase):

    def test_weighted_average_aggregation_error_alpha(self):
        # sum(alpha) = 1.1, error
        alpha = [0.1, 0.2, 0.8]
        with self.assertRaises(NotValidAlphaVectorError):
            weighted_average_aggregation([], alpha)

    def test_weighted_average_aggregation_error_participants_number(self):
        # sum(alpha) = 1, ok
        alpha = [0.1, 0.2, 0.7]
        # empty list for the sake of simplicity
        list_weights = [[], [], [], []]
        with self.assertRaises(NotValidParticipantsModelsError):
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
        with self.assertRaises(NotValidParticipantsModelsError):
            weighted_average_aggregation([w1, w2], alpha)

    @patch(
        "decentralized_smart_grid_ml.contract_interactions.announcement_configuration.AnnouncementConfiguration"
    )
    @patch("pandas.read_csv")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.load_fl_model")
    def test_aggregator_constructor(self, load_fl_model_mock, read_csv_mock, announcement_config_mock):
        participant_ids = [0, 1, 2]
        global_model_path = "/path/to/model"
        announcement_config_mock.fl_rounds = 2
        announcement_config_mock.baseline_model_artifact = global_model_path
        announcement_config_mock.features_names = {
            "features": ["x1", "x2"],
            "labels": "y"
        }
        announcement_config_mock.aggregation_method = "ensemble_general"
        validation_set_path = "/path/to/validation.csv"
        test_set_path = "/path/to/test.csv"
        model_weights_new_round_path = "/path/to/new_model_weights"
        read_csv_mock.side_effect = [
            pd.DataFrame({
                "x1": [0, 1],
                "x2": [1, 2],
                "y": [0, 1]
            }),
            pd.DataFrame({
                "x1": [0, 1],
                "x2": [1, 2],
                "y": [0, 1]
            })
        ]
        model_artifact = "expected model"
        load_fl_model_mock.return_value = model_artifact
        rounds2participants_expected = {
            0: {
                "valid_participant_ids": participant_ids,
                "participant_weights": [],
                "participant_ids": []
            },
            1: {
                "valid_participant_ids": participant_ids,
                "participant_weights": [],
                "participant_ids": []
            }
        }
        aggregator = Aggregator(
            participant_ids,
            announcement_config_mock,
            validation_set_path,
            test_set_path,
            model_weights_new_round_path
        )
        read_csv_mock.has_calls(
            call(test_set_path),
            call(validation_set_path)
        )
        load_fl_model_mock.assert_called_with(global_model_path)
        self.assertDictEqual(rounds2participants_expected, aggregator.rounds2participants)

    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.load_fl_model_weights")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.Aggregator.__init__", return_value=None)
    def test_add_participant_weights(self, aggregator_init_mock, load_fl_model_weights_mock):
        # simulate correct file path for participant 0, round 0
        path_file_created = "/participants/participant_0/weights_round_0.json"
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
        path_file_created = "/participants/participant_0/weights_round_1.json"
        aggregator = Aggregator()
        aggregator.current_round = 0
        is_completed = aggregator.add_participant_weights(path_file_created)
        self.assertEqual(False, is_completed)

    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.load_fl_model_weights")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.Aggregator.__init__", return_value=None)
    def test_add_participant_weights_wrong_participant_id(self, aggregator_init_mock, load_fl_model_weights_mock):
        # simulate wrong file path for not existing participant 1
        path_file_created = "/participants/participant_1/weights_round_0.json"
        aggregator = Aggregator()
        aggregator.current_round = 0
        aggregator.rounds2participants = {
            0: {
                # the participant id 1 is not present in the valid ones
                "valid_participant_ids": [0],
                "participant_weights": [],
                "participant_ids": []
            }
        }
        is_completed = aggregator.add_participant_weights(path_file_created)
        self.assertEqual(False, is_completed)

    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.load_fl_model_weights")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.Aggregator.__init__", return_value=None)
    def test_add_participant_weights_wrong_malformed_path(self, aggregator_init_mock, load_fl_model_weights_mock):
        # simulate wrong file path for not existing participant 1
        path_file_created = "/participants/weights_round_0.json"
        aggregator = Aggregator()
        aggregator.current_round = 0
        is_completed = aggregator.add_participant_weights(path_file_created)
        self.assertEqual(False, is_completed)

    @patch(
        "decentralized_smart_grid_ml.federated_learning.contributions_extractor.ContributionsExtractor"
    )
    @patch(
        "decentralized_smart_grid_ml.contract_interactions.announcement_configuration.AnnouncementConfiguration"
    )
    @patch.object(pathlib.Path, 'mkdir')
    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.weighted_average_aggregation")
    @patch("tensorflow.keras.Sequential")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.save_fl_model_weights")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.Aggregator.__init__", return_value=None)
    def test_update_global_model(self, aggregator_init_mock, save_fl_model_weights_mock,
                                 global_model_mock, weighted_average_aggregation_mock,
                                 mkdir_mock, announcement_config_mock,
                                 contributions_extractor_mock):
        model_weights_new_round_path = "/path/to/new_model_weights/"
        announcement_config_mock.fl_rounds = 2
        validation_results = [0.8, 0.7]
        test_results = [0.8, 0.7]
        x_val = [[2, 1], [3, 4]]
        y_val = [1, 1]
        x_test = [[1, 2], [2, 3]]
        y_test = [0, 1]
        global_model_mock.evaluate.side_effect = (
            validation_results,
            validation_results,
            test_results
        )
        global_weights = [2, 3]
        weighted_average_aggregation_mock.return_value = global_weights
        contributions_extractor_mock.compute_contribution.return_value = [0.5, 0.5]
        aggregator = Aggregator()
        aggregator.current_round = 0
        aggregator.announcement_config = announcement_config_mock
        aggregator.x_test = x_test
        aggregator.y_test = y_test
        aggregator.x_val = x_val
        aggregator.y_val = y_val
        aggregator.is_finished = False
        aggregator.contribution_extractor = contributions_extractor_mock
        aggregator.model_weights_new_round_path = model_weights_new_round_path
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
                "validation_results": validation_results,
                "test_results": validation_results
            }
        }
        aggregator.update_global_model()
        weighted_average_aggregation_mock.assert_called_with(
            [[1, 2], [3, 4]],   # participants' weights
            [0.5, 0.5]          # computed contributions
        )
        global_model_mock.set_weights.assert_called_with(global_weights)
        global_model_mock.evaluate.has_calls(
            call(x_val, y_val),
            call(x_test, y_test),
        )
        save_fl_model_weights_mock.assert_called_with(
            global_model_mock,
            model_weights_new_round_path + "validator_weights_round_1.json",
        )
        self.assertDictEqual(
            rounds2participants_expected,
            aggregator.rounds2participants
        )
        self.assertEqual(1, aggregator.current_round)
        self.assertEqual(False, aggregator.is_finished)

    @patch(
        "decentralized_smart_grid_ml.federated_learning.contributions_extractor.ContributionsExtractor"
    )
    @patch(
        "decentralized_smart_grid_ml.contract_interactions.announcement_configuration.AnnouncementConfiguration"
    )
    @patch.object(pathlib.Path, 'mkdir')
    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.weighted_average_aggregation")
    @patch("tensorflow.keras.Sequential")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.save_fl_model_weights")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.Aggregator.__init__", return_value=None)
    def test_update_global_model_final(self, aggregator_init_mock, save_fl_model_weights_mock,
                                       global_model_mock, weighted_average_aggregation_mock,
                                       mkdir_mock, announcement_config_mock,
                                       contributions_extractor_mock):
        model_weights_new_round_path = "/path/to/new_model_weights/"
        validation_results = ["0.8", "0.7"]
        test_results = ["0.8", "0.7"]
        announcement_config_mock.fl_rounds = 2
        x_val = [[1, 2], [2, 3]]
        y_val = [0, 1]
        x_test = [[1, 2], [2, 3]]
        y_test = [0, 1]
        contributions_extractor_mock.compute_contribution.return_value = [0.5, 0.5]
        global_model_mock.evaluate.side_effect = [
            validation_results,
            test_results
        ]
        global_weights = [2, 3]
        weighted_average_aggregation_mock.return_value = global_weights
        aggregator = Aggregator()
        aggregator.current_round = 1
        aggregator.announcement_config = announcement_config_mock
        aggregator.x_val = x_val
        aggregator.y_val = y_val
        aggregator.x_test = x_test
        aggregator.y_test = y_test
        aggregator.is_finished = False
        aggregator.contribution_extractor = contributions_extractor_mock
        aggregator.model_weights_new_round_path = model_weights_new_round_path
        aggregator.rounds2participants = {
            0: {
                "valid_participant_ids": [0, 1],
                "participant_weights": [[1, 2], [3, 4]],
                "participant_ids": [0, 1],
                "alpha": [0.5, 0.5],
                "validation_results": validation_results,
                "test_results": test_results
            },
            1: {
                "valid_participant_ids": [0, 1],
                "participant_weights": [[1, 2], [3, 4]],
                "participant_ids": [0, 1],
            }
        }
        aggregator.global_model = global_model_mock
        rounds2participants_expected = {
            0: {
                "valid_participant_ids": [0, 1],
                "participant_weights": [[1, 2], [3, 4]],
                "participant_ids": [0, 1],
                "alpha": [0.5, 0.5],
                "validation_results": validation_results,
                "test_results": test_results
            },
            1: {
                "valid_participant_ids": [0, 1],
                "participant_weights": [[1, 2], [3, 4]],
                "participant_ids": [0, 1],
                "alpha": [0.5, 0.5],
                "validation_results": validation_results,
                "test_results": test_results
            }
        }
        aggregator.update_global_model()
        global_model_mock.set_weights.assert_called_with(global_weights)
        global_model_mock.evaluate.has_calls(
            call(x_val, y_val),
            call(x_test, y_test),
        )
        save_fl_model_weights_mock.assert_called_with(
            global_model_mock,
            model_weights_new_round_path + "validator_weights_final.json",
        )
        self.assertDictEqual(
            rounds2participants_expected,
            aggregator.rounds2participants
        )
        self.assertEqual(2, aggregator.current_round)
        self.assertEqual(True, aggregator.is_finished)

    @patch(
        "decentralized_smart_grid_ml.contract_interactions.announcement_configuration.AnnouncementConfiguration"
    )
    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.Aggregator.__init__", return_value=None)
    def test_get_participants_contributions(self, aggregator_init_mock, announcement_config_mock):
        aggregator = Aggregator()
        announcement_config_mock.fl_rounds = 3
        aggregator.announcement_config = announcement_config_mock
        aggregator.participant_ids = [0, 1, 2]
        # here we assume that it is possible to take only a subset of participants
        # for each round (general case)
        aggregator.rounds2participants = {
            0: {
                "participant_ids": [1, 2],
                "alpha": [0.6, 0.4]
            },
            1: {
                "participant_ids": [0, 1, 2],
                "alpha": [0.3, 0.4, 0.3]
            },
            2: {
                "participant_ids": [0, 1],
                "alpha": [0.7, 0.3]
            }
        }
        final_contributions_expected = [0.33, 0.43, 0.23]
        final_contributions = aggregator.get_participants_contributions()
        self.assertListEqual(final_contributions_expected, final_contributions)

    @patch(
        "decentralized_smart_grid_ml.contract_interactions.announcement_configuration.AnnouncementConfiguration"
    )
    @patch("json.dump")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.Aggregator.__init__", return_value=None)
    def test_write_statistics(self, aggregator_init_mock, json_dump_mock, announcement_config_mock):
        file_output_path = "test/output.json"
        m_o = mock_open()
        aggregator = Aggregator()
        announcement_config_mock.fl_rounds = 1
        aggregator.announcement_config = announcement_config_mock
        aggregator.rounds2participants = {
            0: {
                "participant_ids": "test participants ids",
                "alpha": "test alpha",
                "validation_results": "test validation",
                "test_results": "test tests",
                "participant_weights": "test weights",
                "valid_participant_ids": "test valid participant ids"
            }
        }
        statistics_expected = {
            0: {
                "participant_ids": "test participants ids",
                "alpha": "test alpha",
                "validation_results": "test validation",
                "test_results": "test tests",
            }
        }
        with patch('decentralized_smart_grid_ml.federated_learning.federated_aggregator.open', m_o):
            aggregator.write_statistics(file_output_path)
            m_o.assert_called_with(file_output_path, "w")
            handle = m_o()
            json_dump_mock.assert_called_with(statistics_expected, handle, indent="\t")

    @patch(
        "decentralized_smart_grid_ml.federated_learning.contributions_extractor.ContributionsExtractor"
    )
    @patch(
        "decentralized_smart_grid_ml.contract_interactions.announcement_configuration.AnnouncementConfiguration"
    )
    @patch.object(pathlib.Path, 'mkdir')
    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.weighted_average_aggregation")
    @patch("tensorflow.keras.Sequential")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.save_fl_model_weights")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.Aggregator.__init__", return_value=None)
    def test_update_global_model_zero_alpha(
            self, aggregator_init_mock, save_fl_model_weights_mock,
            global_model_mock, weighted_average_aggregation_mock,
            mkdir_mock, announcement_config_mock,
            contributions_extractor_mock):
        model_weights_new_round_path = "/path/to/new_model_weights/"
        validation_results = ["0.8", "0.7"]
        test_results = ["0.8", "0.7"]
        announcement_config_mock.fl_rounds = 2
        x_val = [[1, 2], [2, 3]]
        y_val = [0, 1]
        x_test = [[1, 2], [2, 3]]
        y_test = [0, 1]
        contributions_extractor_mock.compute_contribution.return_value = [0, 0]
        global_model_mock.evaluate.side_effect = [
            validation_results,
            test_results
        ]
        global_weights = [2, 3]
        weighted_average_aggregation_mock.return_value = global_weights
        aggregator = Aggregator()
        aggregator.current_round = 1
        aggregator.announcement_config = announcement_config_mock
        aggregator.x_val = x_val
        aggregator.y_val = y_val
        aggregator.x_test = x_test
        aggregator.y_test = y_test
        aggregator.is_finished = False
        aggregator.contribution_extractor = contributions_extractor_mock
        aggregator.model_weights_new_round_path = model_weights_new_round_path
        aggregator.rounds2participants = {
            0: {
                "valid_participant_ids": [0, 1],
                "participant_weights": [[1, 2], [3, 4]],
                "participant_ids": [0, 1],
                "alpha": [0.5, 0.5],
                "validation_results": validation_results,
                "test_results": test_results
            },
            1: {
                "valid_participant_ids": [0, 1],
                "participant_weights": [[1, 2], [3, 4]],
                "participant_ids": [0, 1],
            }
        }
        aggregator.global_model = global_model_mock
        rounds2participants_expected = {
            0: {
                "valid_participant_ids": [0, 1],
                "participant_weights": [[1, 2], [3, 4]],
                "participant_ids": [0, 1],
                "alpha": [0.5, 0.5],
                "validation_results": validation_results,
                "test_results": test_results
            },
            1: {
                "valid_participant_ids": [0, 1],
                "participant_weights": [[1, 2], [3, 4]],
                "participant_ids": [0, 1],
                "alpha": [0.0, 0.0],
                "validation_results": validation_results,
                "test_results": test_results
            }
        }
        aggregator.update_global_model()
        global_model_mock.evaluate.has_calls(
            call(x_val, y_val),
            call(x_test, y_test),
        )
        self.assertDictEqual(
            rounds2participants_expected,
            aggregator.rounds2participants
        )