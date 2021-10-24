"""
This script is a simple example for the local federated training in the dummy ML task
"""
import argparse
import json
import os
import sys
import time

from web3 import HTTPProvider, Web3

from watchdog.observers import Observer

from decentralized_smart_grid_ml.contract_interactions.announcement_configuration import AnnouncementConfiguration
from decentralized_smart_grid_ml.federated_learning.federated_local_trainer import FederatedLocalTrainer
from decentralized_smart_grid_ml.handlers.participant_handler import ParticipantHandler
from decentralized_smart_grid_ml.utils.bcai_logging import create_logger
from decentralized_smart_grid_ml.utils.config import BLOCKCHAIN_ADDRESS, ANNOUNCEMENT_JSON_PATH, get_address_contract

logger = create_logger(__name__)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--contract_info_path',
        dest='contract_info_path',
        metavar='contract_info_path',
        type=str,
        help="File path to the json file that contains announcement's contract information",
        required=True
    )
    parser.add_argument(
        '--participant_id',
        dest='participant_id',
        metavar='participant_id',
        type=int,
        help='The participant identifier',
        required=True
    )
    parser.add_argument(
        '--validator_directory_path',
        dest='validator_directory_path',
        metavar='validator_directory_path',
        type=str,
        help='The path to the directory that contains the aggregated baseline models for each round',
        required=True
    )

    args = parser.parse_args()
    logger.info("Starting participant %d federated learning", args.participant_id)

    contract_address = get_address_contract(args.contract_info_path)

    # Client instance to interact with the blockchain
    web3 = Web3(HTTPProvider(BLOCKCHAIN_ADDRESS))
    logger.info("Connected to the blockchain %s", BLOCKCHAIN_ADDRESS)

    with open(ANNOUNCEMENT_JSON_PATH) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions

    # Fetch deployed contract reference
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    logger.info("Fetched contract %s", contract_address)

    # automatically takes the idx + 1address
    participant_address = web3.eth.accounts[args.participant_id + 1]
    # extract the Announcement information from the smart contract
    announcement_configuration = AnnouncementConfiguration.retrieve_announcement_configuration(
        participant_address, contract
    )

    participant_directory_path = os.path.join(
        "data_sample",
        announcement_configuration.task_name,
        "participants",
        "participant_" + str(args.participant_id)
    )

    local_dataset_path = os.path.join(
        participant_directory_path,
        announcement_configuration.task_name + "_" + str(args.participant_id) + ".csv"
    )

    federated_local_trainer = FederatedLocalTrainer(
        args.participant_id,
        announcement_configuration,
        local_dataset_path,
        participant_directory_path
    )
    federated_local_trainer.fit_local_model(None)

    participant_handler = ParticipantHandler(federated_local_trainer)
    participant_observer = Observer()
    participant_observer.schedule(participant_handler, args.validator_directory_path, recursive=True)
    # start the observer
    logger.info("Starting the observer for the participant %s", args.participant_id)
    participant_observer.start()
    try:
        while not federated_local_trainer.is_finished:
            time.sleep(1)
    except KeyboardInterrupt:
        # stop and join the observer
        participant_observer.stop()
        participant_observer.join()
    logger.info("The participant %s terminated his work with success", args.participant_id)
    sys.exit(0)
