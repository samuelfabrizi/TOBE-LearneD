import unittest
from unittest.mock import MagicMock, patch, mock_open

from decentralized_smart_grid_ml.contract_interactions.announcement_configuration import AnnouncementConfiguration


class TestAnnouncementConfiguration(unittest.TestCase):

    @patch("json.load")
    def test_retrieve_announcement_configuration(self, json_load_mock):
        m_o = mock_open()
        json_config = {
            "task_name": "test name",
            "task_description": "test description",
            "baseline_model_artifact": "test artifact",
            "baseline_model_weights": "test weights",
            "baseline_model_config": "test config",
            "features_names": "test features",
            "fl_rounds": 2,
            "epochs": 2,
        }
        config_path = "/test/config/path.json"
        fake_address = "address test"
        json_load_mock.return_value = json_config
        contract_mock = MagicMock()
        contract_mock.functions.taskConfiguration().call.return_value = config_path
        with patch("decentralized_smart_grid_ml.contract_interactions.announcement_configuration.open", m_o):
            announcement_config = AnnouncementConfiguration.retrieve_announcement_configuration(fake_address, contract_mock)
        contract_mock.functions.taskConfiguration().call.assert_called_with({"from": fake_address})
        m_o.assert_called_with(config_path, "r")
        handle = m_o()
        json_load_mock.assert_called_with(handle)
        self.assertEqual("test name", announcement_config.task_name)
        self.assertEqual("test description", announcement_config.task_description)
        self.assertEqual("test artifact", announcement_config.baseline_model_artifact)
        self.assertEqual("test weights", announcement_config.baseline_model_weights)
        self.assertEqual("test config", announcement_config.baseline_model_config)
        self.assertEqual("test features", announcement_config.features_names)
        self.assertEqual(2, announcement_config.fl_rounds)
        self.assertEqual(2, announcement_config.epochs)
