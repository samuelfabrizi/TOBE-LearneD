"""
This module contains the functions used to interact with the Announcement Smart Contract
"""
from decentralized_smart_grid_ml.utils.bcai_logging import create_logger

logger = create_logger(__name__)


def announcement_factory(user_address, contract_instance):
    """
    Create a python dictionary representation of an Announcement smart contract
    :param user_address: ethereum address of the user
    :param contract_instance: instance of the Announcement smart contract
    :return: dictionary that contains the Announcement's attributes
    """
    announcement = {
        "n_fl_rounds": contract_instance.functions.flRound().call({"from": user_address}),
        "global_model_path": contract_instance.functions.modelArtifact().call(
            {"from": user_address}
        )
    }
    return announcement
