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

from decentralized_smart_grid_ml.contract_interactions.announcement_factory import announcement_factory
from decentralized_smart_grid_ml.federated_learning.federated_local_trainer import FederatedLocalTrainer
from decentralized_smart_grid_ml.handlers.participant_handler import ParticipantHandler
from decentralized_smart_grid_ml.utils.bcai_logging import create_logger

logger = create_logger(__name__)

# TODO: actually we need to take both epochs and batch size from a configuration file (or the Announcement SC)
EPOCHS = 2

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--participant_id',
        dest='participant_id',
        metavar='participant_id',
        type=int,
        help='The participant identifier',
        required=True
    )
    parser.add_argument(
        '--blockchain_address',
        dest='blockchain_address',
        metavar='blockchain_address',
        type=str,
        help='The address of the blockchain',
        required=True
    )
    parser.add_argument(
        '--announcement_contract_address',
        dest='announcement_contract_address',
        metavar='announcement_contract_address',
        type=str,
        help='The address of the announcement contract',
        required=True
    )
    parser.add_argument(
        '--announcement_json_path',
        dest='announcement_json_path',
        metavar='announcement_json_path',
        type=str,
        help='The file path to the json announcement contract',
        required=True
    )
    parser.add_argument(
        '--task_name',
        dest='task_name',
        metavar='task_name',
        type=str,
        help='The name of the task corresponding to the directory with all the files',
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

    participant_directory_path = os.path.join(
        "data_sample",
        args.task_name,
        "participants",
        "participant_" + str(args.participant_id)
    )

    local_dataset_path = os.path.join(
        participant_directory_path,
        args.task_name + "_" + str(args.participant_id) + ".csv"
    )

    logger.info("Starting participant %d federated learning", args.participant_id)

    # Client instance to interact with the blockchain
    web3 = Web3(HTTPProvider(args.blockchain_address))
    logger.info("Connected to the blockchain %s", args.blockchain_address)

    # Path to the compiled contract JSON file
    compiled_announcement_contract_path = args.announcement_json_path

    with open(compiled_announcement_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions

    # Fetch deployed contract reference
    contract = web3.eth.contract(address=args.announcement_contract_address, abi=contract_abi)
    logger.info("Fetched contract %s", args.announcement_contract_address)

    # automatically takes the idx + 1address
    participant_address = web3.eth.accounts[args.participant_id + 1]
    # extract the Announcement information from the smart contract
    announcement = announcement_factory(participant_address, contract)

    federated_local_trainer = FederatedLocalTrainer(
        args.participant_id,
        announcement,
        local_dataset_path,
        EPOCHS,
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
