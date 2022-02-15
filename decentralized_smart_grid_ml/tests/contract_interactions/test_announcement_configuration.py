import unittest
from unittest.mock import MagicMock, patch, mock_open

from decentralized_smart_grid_ml.contract_interactions.announcement_configuration import AnnouncementConfiguration
from decentralized_smart_grid_ml.exceptions import MalformedConfigurationJson

json_config = {
    "task_name": "test name",
    "task_description": "test description",
    "baseline_model_artifact": "test artifact",
    "baseline_model_weights": "test weights",
    "baseline_model_config": "test config",
    "features_names": "test features",
    "fl_rounds": 2,
    "epochs": 2,
    "batch_size": 32,
    "aggregation_method": "test aggregation"
}


class TestAnnouncementConfiguration(unittest.TestCase):

    @patch("json.load")
    def test_retrieve_announcement_configuration(self, json_load_mock):
        m_o = mock_open()
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
        self.assertEqual("test aggregation", announcement_config.aggregation_method)
        self.assertEqual(2, announcement_config.fl_rounds)
        self.assertEqual(2, announcement_config.epochs)
        self.assertEqual(32, announcement_config.batch_size)

    @patch("json.load")
    def test_retrieve_announcement_configuration_malformed(self, json_load_mock):
        m_o = mock_open()
        config_path = "/test/config/path.json"
        fake_address = "address test"
        json_config_malformed = {
            "task_name": "test name"
        }
        json_load_mock.return_value = json_config_malformed
        contract_mock = MagicMock()
        contract_mock.functions.taskConfiguration().call.return_value = config_path
        with self.assertRaises(MalformedConfigurationJson):
            with patch("decentralized_smart_grid_ml.contract_interactions.announcement_configuration.open", m_o):
                announcement_config = AnnouncementConfiguration.retrieve_announcement_configuration(
                    fake_address,
                    contract_mock
                )

    @patch("json.load")
    def test_write_json_config(self, json_load_mock):
        m_o = mock_open()
        config_path = "/path/to/config.json"
        json_load_mock.return_value = json_config
        with patch("decentralized_smart_grid_ml.contract_interactions.announcement_configuration.open", m_o):
            announcement_config = AnnouncementConfiguration.read_json_config(config_path)
        m_o.assert_called_with(config_path, "r")
        handle = m_o()
        json_load_mock.assert_called_with(handle)
        self.assertEqual("test name", announcement_config.task_name)
        self.assertEqual("test description", announcement_config.task_description)
        self.assertEqual("test artifact", announcement_config.baseline_model_artifact)
        self.assertEqual("test weights", announcement_config.baseline_model_weights)
        self.assertEqual("test config", announcement_config.baseline_model_config)
        self.assertEqual("test features", announcement_config.features_names)
        self.assertEqual("test aggregation", announcement_config.aggregation_method)
        self.assertEqual(2, announcement_config.fl_rounds)
        self.assertEqual(2, announcement_config.epochs)
        self.assertEqual(32, announcement_config.batch_size)
