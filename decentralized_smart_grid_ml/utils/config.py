"""
This module contains all the global shared config needed by Decentralized-SG framework
"""
import json
import os

BLOCKCHAIN_ADDRESS = os.environ["BC_ADDRESS"]
ANNOUNCEMENT_JSON_PATH = os.environ["ANNOUNCEMENT_JSON_PATH"]
DEX_JSON_PATH = os.environ["DEX_JSON_PATH"]
TOKEN_JSON_PATH = os.environ["TOKEN_JSON_PATH"]


def get_addresses_contracts(contract_info_path):
    """
    Returns the address of the deployed contracts
    :param contract_info_path: File path to the json file that contains information about the contract
    :return: (address of the Announcement contract, address of the GreenDEX contract)
    """
    with open(contract_info_path, "r") as file_read:
        json_info_path = json.load(file_read)
    announcement_address = json_info_path["address"]
    dex_address = json_info_path["address_dex"]
    return announcement_address, dex_address
