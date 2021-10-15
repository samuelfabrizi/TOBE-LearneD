import unittest
from unittest.mock import patch

import pandas as pd

from decentralized_smart_grid_ml.federated_learning.federated_local_trainer import FederatedLocalTrainer


class TestFederatedLocalTrainer(unittest.TestCase):

    @patch("pandas.read_csv")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_local_trainer.load_fl_model")
    def test_aggregator_constructor(self, load_fl_model_mock, read_csv_mock):
        client_id = 0
        n_fl_rounds = 2
        global_model_path = "/path/to/model"
        train_set_path = "/path/to/train.csv"
        n_epochs = 5
        local_model_weights_path = "/path/to/client_directory"
        read_csv_mock.return_value = pd.DataFrame({
            "x1": [0, 1],
            "x2": [1, 2],
            "y": [0, 1]
        })
        model_artifact = "expected model"
        load_fl_model_mock.return_value = model_artifact
        rounds2history_expected = {
            0: None,
            1: None
        }
        flt = FederatedLocalTrainer(
            client_id,
            n_fl_rounds,
            global_model_path,
            train_set_path,
            n_epochs,
            local_model_weights_path
        )
        read_csv_mock.assert_called_with(train_set_path)
        load_fl_model_mock.assert_called_with(global_model_path)
        self.assertDictEqual(rounds2history_expected, flt.rounds2history)
