import unittest
from unittest.mock import patch

from decentralized_smart_grid_ml.handlers.validator_handler import ValidatorHandler


class TestValidatorHandler(unittest.TestCase):

    def test_validator_constructor(self):
        val_handler = ValidatorHandler("aggregator")
        self.assertEqual(val_handler.aggregator, "aggregator")

    @patch("watchdog.events.FileSystemEvent")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.Aggregator")
    def test_on_created_false(self, aggregator_mock, event_mock):
        path_to_local_weights = "/path/to/client_weights.json"
        event_mock.src_path = path_to_local_weights
        aggregator_mock.add_participant_weights.return_value = False
        val_handler = ValidatorHandler(aggregator_mock)
        val_handler.on_created(event_mock)
        aggregator_mock.add_participant_weights.assert_called_with(path_to_local_weights)

    @patch("watchdog.events.FileSystemEvent")
    @patch("decentralized_smart_grid_ml.federated_learning.federated_aggregator.Aggregator")
    def test_on_created(self, aggregator_mock, event_mock):
        path_to_local_weights = "/path/to/client_weights.json"
        event_mock.src_path = path_to_local_weights
        aggregator_mock.add_participant_weights.return_value = True
        val_handler = ValidatorHandler(aggregator_mock)
        val_handler.on_created(event_mock)
        aggregator_mock.add_participant_weights.assert_called_with(path_to_local_weights)
        aggregator_mock.update_global_model.assert_called_once()
