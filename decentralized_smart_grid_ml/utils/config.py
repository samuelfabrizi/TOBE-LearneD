"""
This module contains all the global shared config needed by Decentralized-SG framework
"""
import json
import os


CURRENT_PATH_SPLIT = os.path.dirname(os.path.abspath(__file__)).split("/")
PROJECT_ABSOLUTE_PATH = "/".join(CURRENT_PATH_SPLIT[:-2])

BLOCKCHAIN_ADDRESS = os.environ["BC_ADDRESS"]
ANNOUNCEMENT_JSON_PATH = PROJECT_ABSOLUTE_PATH + "/build/contracts/Announcement.json"
DEX_JSON_PATH = PROJECT_ABSOLUTE_PATH + "/build/contracts/GreenDEX.json"
TOKEN_JSON_PATH = PROJECT_ABSOLUTE_PATH + "/build/contracts/GreenToken.json"


def get_addresses_contracts(contract_info_path):
    """
    Returns the address of the deployed contracts
    :param contract_info_path: File path to the json file that contains information about
        the contract
    :return: (address of the Announcement contract, address of the GreenDEX contract)
    """
    with open(contract_info_path, "r") as file_read:
        json_info_path = json.load(file_read)
    announcement_address = json_info_path["address"]
    dex_address = json_info_path["address_dex"]
    return announcement_address, dex_address
