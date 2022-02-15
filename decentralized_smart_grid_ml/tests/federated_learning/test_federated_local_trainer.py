import pathlib
import unittest
from unittest.mock import patch, mock_open, MagicMock

import pandas as pd

from decentralized_smart_grid_ml.federated_learning.federated_local_trainer import FederatedLocalTrainer


class TestFederatedLocalTrainer(unittest.TestCase):

    @patch(
        "decentralized_smart_grid_ml.contract_interactions.announcement_configuration.AnnouncementConfiguration"
    )
    @patch("pandas.read_csv")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_local_trainer.load_fl_model")
    def test_federated_local_trainer_constructor(self, load_fl_model_mock, read_csv_mock,
                                                 announcement_config_mock):
        participant_id = 0
        announcement_config_mock.fl_rounds = 2
        announcement_config_mock.epochs = 5
        announcement_config_mock.batch_size = 32
        announcement_config_mock.baseline_model_artifact = "/path/to/model"
        announcement_config_mock.features_names = {
            "features": ["x1", "x2"],
            "labels": "y"
        }
        train_set_path = "/path/to/train.csv"
        local_model_weights_path = "/path/to/participant_directory"
        read_csv_mock.return_value = pd.DataFrame({
            "x1": [0, 1],
            "x2": [1, 2],
            "y": [0, 1]
        })
        model_artifact = "expected local model"
        load_fl_model_mock.return_value = model_artifact
        rounds2history_expected = {
            0: None,
            1: None
        }
        flt = FederatedLocalTrainer(
            participant_id,
            announcement_config_mock,
            train_set_path,
            local_model_weights_path
        )
        read_csv_mock.assert_called_with(train_set_path)
        load_fl_model_mock.assert_called_with("/path/to/model")
        self.assertEqual(model_artifact, flt.local_model)
        self.assertEqual(0, flt.current_round)
        self.assertDictEqual(rounds2history_expected, flt.rounds2history)

    @patch(
        "decentralized_smart_grid_ml.contract_interactions.announcement_configuration.AnnouncementConfiguration"
    )
    @patch.object(pathlib.Path, 'mkdir')
    @patch("tensorflow.keras.Sequential")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_local_trainer.save_fl_model_weights")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_local_trainer.load_fl_model_weights")
    @patch(
        "decentralized_smart_grid_ml.federated_learning.federated_local_trainer.FederatedLocalTrainer.__init__",
        return_value=None
    )
    def test_fit_local_model_completed(self, federated_local_trainer_mock, load_fl_model_weights_mock,
                                       save_fl_model_weights_mock, local_model_mock, mkdir_mock,
                                       announcement_config_mock):
        current_round = 1
        announcement_config_mock.fl_rounds = 2
        announcement_config_mock.epochs = 5
        announcement_config_mock.batch_size = 32
        path_file_created = "validator/validator_weights_round_1.json"
        baseline_model_weights = "baseline model weights"
        x_train = "train x"
        y_train = "train y"
        local_model_weights_path = "participants/participant_0/"
        local_model_trained_path = local_model_weights_path + "weights_round_" + str(current_round) + ".json"
        load_fl_model_weights_mock.return_value = baseline_model_weights
        expected_history = "history 1"
        expected_history_mock = MagicMock()
        expected_history_mock.history = expected_history
        rounds2history_expected = {
            0: None,
            1: expected_history
        }
        local_model_mock.fit.return_value = expected_history_mock
        flt = FederatedLocalTrainer()
        flt.x_train = x_train
        flt.y_train = y_train
        flt.current_round = current_round
        flt.local_model = local_model_mock
        flt.participant_id = 0
        flt.announcement_config = announcement_config_mock
        flt.local_model_weights_path = local_model_weights_path
        flt.rounds2history = {
            0: None,
            1: None
        }
        is_completed = flt.fit_local_model(path_file_created)
        local_model_mock.fit.assert_called_with(
            x_train, y_train,
            epochs=announcement_config_mock.epochs,
            batch_size=announcement_config_mock.batch_size
        )
        local_model_mock.set_weights.assert_called_with(baseline_model_weights)
        save_fl_model_weights_mock.assert_called_with(local_model_mock, local_model_trained_path)
        self.assertDictEqual(rounds2history_expected, flt.rounds2history)
        self.assertEqual(True, is_completed)

    @patch(
        "decentralized_smart_grid_ml.contract_interactions.announcement_configuration.AnnouncementConfiguration"
    )
    @patch.object(pathlib.Path, 'mkdir')
    @patch("tensorflow.keras.Sequential")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_local_trainer.save_fl_model_weights")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_local_trainer.load_fl_model_weights")
    @patch(
        "decentralized_smart_grid_ml.federated_learning.federated_local_trainer.FederatedLocalTrainer.__init__",
        return_value=None
    )
    def test_fit_local_model_not_completed(self, federated_local_trainer_mock, load_fl_model_weights_mock,
                                           save_fl_model_weights_mock, local_model_mock, mkdir_mock,
                                           announcement_config_mock):
        current_round = 1
        announcement_config_mock.fl_rounds = 3
        announcement_config_mock.epochs = 5
        announcement_config_mock.batch_size = 32
        path_file_created = "validator/validator_weights_round_1.json"
        baseline_model_weights = "baseline model weights"
        x_train = "train x"
        y_train = "train y"
        local_model_weights_path = "participants/participant_0/"
        local_model_trained_path = local_model_weights_path + "weights_round_" + str(current_round) + ".json"
        load_fl_model_weights_mock.return_value = baseline_model_weights
        expected_history = "history 1"
        expected_history_mock = MagicMock()
        expected_history_mock.history = expected_history
        rounds2history_expected = {
            0: None,
            1: expected_history,
            2: None,
        }
        local_model_mock.fit.return_value = expected_history_mock
        flt = FederatedLocalTrainer()
        flt.x_train = x_train
        flt.y_train = y_train
        flt.current_round = current_round
        flt.local_model = local_model_mock
        flt.participant_id = 0
        flt.announcement_config = announcement_config_mock
        flt.local_model_weights_path = local_model_weights_path
        flt.rounds2history = {
            0: None,
            1: None,
            2: None
        }
        is_completed = flt.fit_local_model(path_file_created)
        local_model_mock.fit.assert_called_with(
            x_train, y_train,
            epochs=announcement_config_mock.epochs,
            batch_size=announcement_config_mock.batch_size
        )
        local_model_mock.set_weights.assert_called_with(baseline_model_weights)
        save_fl_model_weights_mock.assert_called_with(local_model_mock, local_model_trained_path)
        self.assertEqual(False, is_completed)
        self.assertDictEqual(rounds2history_expected, flt.rounds2history)

    @patch(
        "decentralized_smart_grid_ml.contract_interactions.announcement_configuration.AnnouncementConfiguration"
    )
    @patch.object(pathlib.Path, 'mkdir')
    @patch("tensorflow.keras.Sequential")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_local_trainer.save_fl_model_weights")
    @patch(
        "decentralized_smart_grid_ml.federated_learning.federated_local_trainer.FederatedLocalTrainer.__init__",
        return_value=None
    )
    def test_fit_local_model_first_round(self, federated_local_trainer_mock, save_fl_model_weights_mock,
                                         local_model_mock, mkdir_mock, announcement_config_mock):
        current_round = 0
        announcement_config_mock.fl_rounds = 2
        announcement_config_mock.epochs = 5
        announcement_config_mock.batch_size = 32
        x_train = "train x"
        y_train = "train y"
        local_model_weights_path = "participants/participant_0/"
        local_model_trained_path = local_model_weights_path + "weights_round_" + str(current_round) + ".json"
        expected_history = "history 1"
        expected_history_mock = MagicMock()
        expected_history_mock.history = expected_history
        rounds2history_expected = {
            0: expected_history,
            1: None
        }
        local_model_mock.fit.return_value = expected_history_mock
        flt = FederatedLocalTrainer()
        flt.x_train = x_train
        flt.y_train = y_train
        flt.current_round = current_round
        flt.local_model = local_model_mock
        flt.participant_id = 0
        flt.announcement_config = announcement_config_mock
        flt.local_model_weights_path = local_model_weights_path
        flt.rounds2history = {
            0: None,
            1: None
        }
        # we pass None because it is the first round
        is_completed = flt.fit_local_model(None)
        local_model_mock.fit.assert_called_with(
            x_train, y_train,
            epochs=announcement_config_mock.epochs,
            batch_size=announcement_config_mock.batch_size
        )
        save_fl_model_weights_mock.assert_called_with(local_model_mock, local_model_trained_path)
        self.assertEqual(False, is_completed)
        self.assertDictEqual(rounds2history_expected, flt.rounds2history)

    @patch(
        "decentralized_smart_grid_ml.contract_interactions.announcement_configuration.AnnouncementConfiguration"
    )
    @patch(
        "decentralized_smart_grid_ml.federated_learning.federated_local_trainer.FederatedLocalTrainer.__init__",
        return_value=None
    )
    def test_fit_local_model_malformed_path(self, federated_local_trainer_mock, announcement_config_mock):
        current_round = 1
        announcement_config_mock.fl_rounds = 2
        path_file_created = "validator/validator_weights_round_null.json"
        flt = FederatedLocalTrainer()
        flt.current_round = current_round
        flt.announcement_config = announcement_config_mock
        flt.participant_id = 0
        is_completed = flt.fit_local_model(path_file_created)
        self.assertEqual(False, is_completed)

    @patch(
        "decentralized_smart_grid_ml.contract_interactions.announcement_configuration.AnnouncementConfiguration"
    )
    @patch(
        "decentralized_smart_grid_ml.federated_learning.federated_local_trainer.FederatedLocalTrainer.__init__",
        return_value=None
    )
    def test_fit_local_model_wrong_round(self, federated_local_trainer_mock, announcement_config_mock):
        current_round = 1
        announcement_config_mock.fl_rounds = 2
        path_file_created = "validator/validator_weights_round_0.json"
        flt = FederatedLocalTrainer()
        flt.current_round = current_round
        flt.announcement_config = announcement_config_mock
        flt.participant_id = 0
        is_completed = flt.fit_local_model(path_file_created)
        self.assertEqual(False, is_completed)

    @patch(
        "decentralized_smart_grid_ml.contract_interactions.announcement_configuration.AnnouncementConfiguration"
    )
    @patch("json.dump")
    @patch(
        "decentralized_smart_grid_ml.federated_learning.federated_local_trainer.FederatedLocalTrainer.__init__",
        return_value=None
    )
    def test_write_statistics(self, federated_local_trainer_mock, json_dump_mock, announcement_config_mock):
        m_o = mock_open()
        file_output_path = "test/output.json"
        announcement_config_mock.fl_rounds = 1
        flt = FederatedLocalTrainer()
        flt.announcement_config = announcement_config_mock
        flt.participant_id = 0
        flt.rounds2history = {
            0: "history test"
        }
        statistics_expected = {
            0: "history test"
        }
        with patch('decentralized_smart_grid_ml.federated_learning.federated_local_trainer.open', m_o):
            flt.write_statistics(file_output_path)
            m_o.assert_called_with(file_output_path, "w")
            handle = m_o()
            json_dump_mock.assert_called_with(statistics_expected, handle, indent="\t")
