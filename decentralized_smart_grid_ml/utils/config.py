"""
This module contains all the global shared config needed by Decentralized-SG framework
"""
import json
import os

BLOCKCHAIN_ADDRESS = os.environ["BC_ADDRESS"]
ANNOUNCEMENT_JSON_PATH = os.environ["ANNOUNCEMENT_JSON_PATH"]


def get_address_contract(contract_info_path):
    """
    Returns the address of the contract
    :param contract_info_path: File path to the json file that contains information about the contract
    :return:
    """
    with open(contract_info_path, "r") as file_read:
        json_info_path = json.load(file_read)
    return json_info_path["address"]
