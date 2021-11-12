import unittest
from unittest.mock import patch

from decentralized_smart_grid_ml.handlers.participant_handler import ParticipantHandler


class TestParticipantHandler(unittest.TestCase):

    @patch("watchdog.events.FileSystemEvent")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_local_trainer.FederatedLocalTrainer")
    def test_on_created(self, trainer_mock, event_mock):
        path_to_aggregated_weights = "/path/to/aggregated_weights.json"
        event_mock.src_path = path_to_aggregated_weights
        trainer_mock.is_finished = False
        trainer_mock.fit_local_model.return_value = False
        val_handler = ParticipantHandler(trainer_mock)
        val_handler.on_created(event_mock)
        trainer_mock.fit_local_model.assert_called_with(path_to_aggregated_weights)

    @patch("watchdog.events.FileSystemEvent")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_local_trainer.FederatedLocalTrainer")
    def test_on_created_completed(self, trainer_mock, event_mock):
        path_to_aggregated_weights = "/path/to/aggregated_weights.json"
        event_mock.src_path = path_to_aggregated_weights
        trainer_mock.is_finished = False
        trainer_mock.fit_local_model.return_value = True
        val_handler = ParticipantHandler(trainer_mock)
        val_handler.on_created(event_mock)
        trainer_mock.fit_local_model.assert_called_with(path_to_aggregated_weights)
