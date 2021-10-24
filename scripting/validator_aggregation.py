"""
This script runs the Federate Learning life cycle of the validator
"""
import argparse
import json
import sys
import time

from watchdog.observers import Observer
from web3 import Web3, HTTPProvider

from decentralized_smart_grid_ml.contract_interactions.announcement_configuration import \
    AnnouncementConfiguration
from decentralized_smart_grid_ml.federated_learning.federated_aggregator import Aggregator
from decentralized_smart_grid_ml.handlers.validator_handler import ValidatorHandler
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
        '--test_set_path',
        dest='test_set_path',
        metavar='test_set_path',
        type=str,
        help='The file path to the test set',
        required=True
    )
    parser.add_argument(
        '--model_weights_new_round_path',
        dest='model_weights_new_round_path',
        metavar='model_weights_new_round_path',
        type=str,
        help="The directory path to the model's weights for each round",
        required=True
    )
    # TODO: this argument has to be removed when we implemented the communication between
    #       validator and participants
    parser.add_argument(
        '--participant_weights_path',
        dest='participant_weights_path',
        metavar='participant_weights_path',
        type=str,
        help="The directory path that contains the sub-directories for the "
             "weights of the local trained participants' models",
        required=True
    )

    args = parser.parse_args()
    logger.info("Starting validator job")

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

    # automatically takes the last address
    validator_address = web3.eth.accounts[-1]
    # extract the Announcement information from the smart contract
    announcement_configuration = AnnouncementConfiguration.retrieve_announcement_configuration(
        validator_address, contract
    )

    maximum_number_participants = contract.functions.maxNumberParticipant().call({"from": validator_address})
    isStarted = False

    while not isStarted:
        number_participants = contract.functions.currentNumberParticipant().call({"from": validator_address})
        if number_participants != maximum_number_participants:
            logger.info("We need to wait that other participants subscribe to the task")
            time.sleep(2)
        else:
            isStarted = True

    aggregator = Aggregator(
        list(range(number_participants)),
        announcement_configuration,
        args.test_set_path,
        args.model_weights_new_round_path
    )
    aggregator_handler = ValidatorHandler(aggregator=aggregator)
    path = "."
    go_recursively = True

    validator_observer = Observer()
    validator_observer.schedule(aggregator_handler, args.participant_weights_path, recursive=True)
    # start the observer
    logger.info("Starting the observer for the validator")
    validator_observer.start()
    try:
        while not aggregator.is_finished:
            time.sleep(1)
    except KeyboardInterrupt:
        # stop and join the observer
        validator_observer.stop()
        validator_observer.join()
    logger.info("The validator terminated his work with success")
    sys.exit(0)
