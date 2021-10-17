import unittest
from unittest.mock import MagicMock

from decentralized_smart_grid_ml.contract_interactions.announcement_factory import announcement_factory


class TestAnnouncementFactory(unittest.TestCase):

    def test_announcement_factory(self):
        n_fl_rounds = 2
        global_model_path = "path/to/global/model"
        fake_address = "address test"
        announcement_expected = {
            "n_fl_rounds": n_fl_rounds,
            "global_model_path": global_model_path
        }
        contract_mock = MagicMock()
        contract_mock.functions.flRound().call.return_value = n_fl_rounds
        contract_mock.functions.modelArtifact().call.return_value = global_model_path
        announcement = announcement_factory(fake_address, contract_mock)
        contract_mock.functions.flRound().call.assert_called_with({"from": fake_address})
        contract_mock.functions.modelArtifact().call.assert_called_with({"from": fake_address})
        self.assertDictEqual(announcement_expected, announcement)
