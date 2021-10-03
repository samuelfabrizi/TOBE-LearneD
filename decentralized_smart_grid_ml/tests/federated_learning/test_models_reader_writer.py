import unittest
from unittest.mock import patch, mock_open

import numpy as np

from decentralized_smart_grid_ml.exceptions import IncorrectExtensionFileError
from decentralized_smart_grid_ml.federated_learning.models_reader_writer import save_fl_model, load_fl_model, \
    save_fl_model_config, load_fl_model_config, save_fl_model_weights, load_fl_model_weights


class TestModelsReaderWriter(unittest.TestCase):

    def test_save_fl_model(self):
        model_path = "/path/to/model"
        with patch("tensorflow.keras.Sequential") as model_mock:
            save_fl_model(model_mock, model_path)
            model_mock.save.assert_called_with(model_path)

    def test_load_fl_model(self):
        model_path = "/path/to/model"
        expected_model = "test_model"
        with patch("tensorflow.keras.models.load_model") as load_model_mock:
            load_model_mock.return_value = expected_model
            model = load_fl_model(model_path)
            load_model_mock.assert_called_with(model_path)
        self.assertEqual(expected_model, model)

    @patch('json.dump')
    def test_save_fl_model_config(self, json_dump_mock):
        m_o = mock_open()
        expected_json_dict = {
            "class_name": "LinearModel",
            "config": {
                "test_layer": "layer"
            }
        }
        model_path = "/path/to/model.json"
        model_config_json = '{"class_name": "LinearModel", ' \
                            '"config": {"test_layer": "layer"}}'
        with patch("tensorflow.keras.Sequential") as model_mock:
            with patch('decentralized_smart_grid_ml.federated_learning.models_reader_writer.open', m_o):
                model_mock.to_json.return_value = model_config_json
                save_fl_model_config(model_mock, model_path)
                m_o.assert_called_with(model_path, "w")
                handle = m_o()
                json_dump_mock.assert_called_with(expected_json_dict, handle, indent=1)

    def test_save_fl_model_config_no_json(self):
        model_path = "/path/to/model.txt"
        with patch("tensorflow.keras.Sequential") as model_mock:
            with self.assertRaises(IncorrectExtensionFileError):
                save_fl_model_config(model_mock, model_path)

    @patch('json.load')
    def test_load_fl_model_config(self, json_load_mock):
        m_o = mock_open()
        model_config = {
            "class_name": "LinearModel",
            "config": {
                "test_layer": "layer"
            }
        }
        expected_model_config_json_str = '{"class_name": "LinearModel", ' \
                                         '"config": {"test_layer": "layer"}}'
        json_load_mock.return_value = model_config
        model_path = "/path/to/model.json"
        with patch('decentralized_smart_grid_ml.federated_learning.models_reader_writer.open', m_o):
            with patch("tensorflow.keras.models.model_from_json") as model_from_json_mock:
                load_fl_model_config(model_path)
                m_o.assert_called_with(model_path, "r")
                model_from_json_mock.assert_called_with(expected_model_config_json_str)

    def test_load_fl_model_config_no_json(self):
        model_path = "/path/to/model.txt"
        with self.assertRaises(IncorrectExtensionFileError):
            load_fl_model_config(model_path)

    @patch('json.dump')
    def test_save_fl_model_weights(self, json_dump_mock):
        m_o = mock_open()
        model_weights = [
            np.array([1, 2, 3, 4]),
            np.array([1, 2]),
        ]
        expected_weights_json = [
            [1, 2, 3, 4],
            [1, 2]
        ]
        model_weights_path = "/path/to/model_weights.json"
        with patch("tensorflow.keras.Sequential") as model_mock:
            with patch('decentralized_smart_grid_ml.federated_learning.models_reader_writer.open', m_o):
                model_mock.get_weights.return_value = model_weights
                save_fl_model_weights(model_mock, model_weights_path)
                m_o.assert_called_with(model_weights_path, "w")
                handle = m_o()
                json_dump_mock.assert_called_with(expected_weights_json, handle, indent=1)

    def test_save_fl_model_weights_no_json(self):
        model_weights_path = "/path/to/model_weights.txt"
        with patch("tensorflow.keras.Sequential") as model_mock:
            with self.assertRaises(IncorrectExtensionFileError):
                save_fl_model_weights(model_mock, model_weights_path)

    @patch('json.load')
    def test_load_fl_model_weights(self, json_load_mock):
        m_o = mock_open()
        model_weights_path = "/path/to/model_weights.json"
        weights_json = [
            [1, 2, 3, 4],
            [1, 2]
        ]
        expected_model_weights = [
            np.array([1, 2, 3, 4]),
            np.array([1, 2]),
        ]
        json_load_mock.return_value = weights_json
        with patch('decentralized_smart_grid_ml.federated_learning.models_reader_writer.open', m_o):
            model_weights = load_fl_model_weights(model_weights_path)
            m_o.assert_called_with(model_weights_path, "r")
            handle = m_o()
            json_load_mock.assert_called_with(handle)
            for expected_layer_weights, layer_weights in zip(expected_model_weights, model_weights):
                np.testing.assert_array_equal(expected_layer_weights, layer_weights)

    def test_load_fl_model_weights_no_json(self):
        model_weights_path = "/path/to/model_weights.txt"
        with self.assertRaises(IncorrectExtensionFileError):
            load_fl_model_weights(model_weights_path)