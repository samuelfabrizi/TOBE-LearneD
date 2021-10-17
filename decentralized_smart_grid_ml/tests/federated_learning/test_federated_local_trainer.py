import pathlib
import unittest
from unittest.mock import patch

import pandas as pd

from decentralized_smart_grid_ml.federated_learning.federated_local_trainer import FederatedLocalTrainer


class TestFederatedLocalTrainer(unittest.TestCase):

    @patch("pandas.read_csv")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_local_trainer.load_fl_model")
    def test_federated_local_trainer_constructor(self, load_fl_model_mock, read_csv_mock):
        participant_id = 0
        n_fl_rounds = 2
        global_model_path = "/path/to/model"
        train_set_path = "/path/to/train.csv"
        n_epochs = 5
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
            n_fl_rounds,
            global_model_path,
            train_set_path,
            n_epochs,
            local_model_weights_path
        )
        read_csv_mock.assert_called_with(train_set_path)
        load_fl_model_mock.assert_called_with(global_model_path)
        self.assertEqual(model_artifact, flt.local_model)
        self.assertEqual(0, flt.current_round)
        self.assertDictEqual(rounds2history_expected, flt.rounds2history)

    @patch.object(pathlib.Path, 'mkdir')
    @patch("tensorflow.keras.Sequential")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_local_trainer.save_fl_model_weights")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_local_trainer.load_fl_model_weights")
    @patch(
        "decentralized_smart_grid_ml.federated_learning.federated_local_trainer.FederatedLocalTrainer.__init__",
        return_value=None
    )
    def test_fit_local_model_completed(self, federated_local_trainer_mock, load_fl_model_weights_mock,
                                       save_fl_model_weights_mock, local_model_mock, mkdir_mock):
        current_round = 1
        n_fl_rounds = 2
        path_file_created = "validator/validator_weights_round_1.json"
        baseline_model_weights = "baseline model weights"
        x_train = "train x"
        y_train = "train y"
        n_epochs = 5
        local_model_weights_path = "participants/participant_0/"
        local_model_trained_path = local_model_weights_path + "weights_round_" + str(current_round) + ".json"
        load_fl_model_weights_mock.return_value = baseline_model_weights
        expected_history = "history 1"
        rounds2history_expected = {
            0: None,
            1: expected_history
        }
        local_model_mock.fit.return_value = expected_history
        flt = FederatedLocalTrainer()
        flt.x_train = x_train
        flt.y_train = y_train
        flt.epochs = n_epochs
        flt.current_round = current_round
        flt.local_model = local_model_mock
        flt.participant_id = 0
        flt.n_fl_rounds = n_fl_rounds
        flt.local_model_weights_path = local_model_weights_path
        flt.rounds2history = {
            0: None,
            1: None
        }
        is_completed = flt.fit_local_model(path_file_created)
        local_model_mock.fit.assert_called_with(x_train, y_train, epochs=n_epochs)
        local_model_mock.set_weights.assert_called_with(baseline_model_weights)
        save_fl_model_weights_mock.assert_called_with(local_model_mock, local_model_trained_path)
        self.assertDictEqual(rounds2history_expected, flt.rounds2history)
        self.assertEqual(True, is_completed)

    @patch.object(pathlib.Path, 'mkdir')
    @patch("tensorflow.keras.Sequential")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_local_trainer.save_fl_model_weights")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_local_trainer.load_fl_model_weights")
    @patch(
        "decentralized_smart_grid_ml.federated_learning.federated_local_trainer.FederatedLocalTrainer.__init__",
        return_value=None
    )
    def test_fit_local_model_not_completed(self, federated_local_trainer_mock, load_fl_model_weights_mock,
                                           save_fl_model_weights_mock, local_model_mock, mkdir_mock):
        current_round = 1
        n_fl_rounds = 3
        path_file_created = "validator/validator_weights_round_1.json"
        baseline_model_weights = "baseline model weights"
        x_train = "train x"
        y_train = "train y"
        n_epochs = 5
        local_model_weights_path = "participants/participant_0/"
        local_model_trained_path = local_model_weights_path + "weights_round_" + str(current_round) + ".json"
        load_fl_model_weights_mock.return_value = baseline_model_weights
        expected_history = "history 1"
        rounds2history_expected = {
            0: None,
            1: expected_history,
            2: None,
        }
        local_model_mock.fit.return_value = expected_history
        flt = FederatedLocalTrainer()
        flt.x_train = x_train
        flt.y_train = y_train
        flt.epochs = n_epochs
        flt.current_round = current_round
        flt.local_model = local_model_mock
        flt.participant_id = 0
        flt.n_fl_rounds = n_fl_rounds
        flt.local_model_weights_path = local_model_weights_path
        flt.rounds2history = {
            0: None,
            1: None,
            2: None
        }
        is_completed = flt.fit_local_model(path_file_created)
        local_model_mock.fit.assert_called_with(x_train, y_train, epochs=n_epochs)
        local_model_mock.set_weights.assert_called_with(baseline_model_weights)
        save_fl_model_weights_mock.assert_called_with(local_model_mock, local_model_trained_path)
        self.assertEqual(False, is_completed)
        self.assertDictEqual(rounds2history_expected, flt.rounds2history)

    @patch.object(pathlib.Path, 'mkdir')
    @patch("tensorflow.keras.Sequential")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_local_trainer.save_fl_model_weights")
    @patch(
        "decentralized_smart_grid_ml.federated_learning.federated_local_trainer.FederatedLocalTrainer.__init__",
        return_value=None
    )
    def test_fit_local_model_first_round(self, federated_local_trainer_mock, save_fl_model_weights_mock,
                                         local_model_mock, mkdir_mock):
        current_round = 0
        n_fl_rounds = 2
        x_train = "train x"
        y_train = "train y"
        n_epochs = 5
        local_model_weights_path = "participants/participant_0/"
        local_model_trained_path = local_model_weights_path + "weights_round_" + str(current_round) + ".json"
        expected_history = "history 1"
        rounds2history_expected = {
            0: expected_history,
            1: None
        }
        local_model_mock.fit.return_value = expected_history
        flt = FederatedLocalTrainer()
        flt.x_train = x_train
        flt.y_train = y_train
        flt.epochs = n_epochs
        flt.current_round = current_round
        flt.local_model = local_model_mock
        flt.participant_id = 0
        flt.n_fl_rounds = n_fl_rounds
        flt.local_model_weights_path = local_model_weights_path
        flt.rounds2history = {
            0: None,
            1: None
        }
        # we pass None because it is the first round
        is_completed = flt.fit_local_model(None)
        local_model_mock.fit.assert_called_with(x_train, y_train, epochs=n_epochs)
        save_fl_model_weights_mock.assert_called_with(local_model_mock, local_model_trained_path)
        self.assertEqual(False, is_completed)
        self.assertDictEqual(rounds2history_expected, flt.rounds2history)

    @patch(
        "decentralized_smart_grid_ml.federated_learning.federated_local_trainer.FederatedLocalTrainer.__init__",
        return_value=None
    )
    def test_fit_local_model_malformed_path(self, federated_local_trainer_mock):
        current_round = 1
        path_file_created = "validator/validator_weights_round_null.json"
        flt = FederatedLocalTrainer()
        flt.current_round = current_round
        flt.n_fl_rounds = 2
        flt.participant_id = 0
        is_completed = flt.fit_local_model(path_file_created)
        self.assertEqual(False, is_completed)

    @patch(
        "decentralized_smart_grid_ml.federated_learning.federated_local_trainer.FederatedLocalTrainer.__init__",
        return_value=None
    )
    def test_fit_local_model_wront_round(self, federated_local_trainer_mock):
        current_round = 1
        path_file_created = "validator/validator_weights_round_0.json"
        flt = FederatedLocalTrainer()
        flt.current_round = current_round
        flt.n_fl_rounds = 2
        flt.participant_id = 0
        is_completed = flt.fit_local_model(path_file_created)
        self.assertEqual(False, is_completed)