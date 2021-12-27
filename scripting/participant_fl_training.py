"""
This script is a simple example for the local federated training in the dummy ML task
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

from numpy.random import rand
from web3 import HTTPProvider, Web3

from watchdog.observers import Observer

from decentralized_smart_grid_ml.contract_interactions.announcement_configuration import AnnouncementConfiguration
from decentralized_smart_grid_ml.federated_learning.federated_local_trainer import FederatedLocalTrainer
from decentralized_smart_grid_ml.federated_learning.models_reader_writer import load_fl_model_weights, \
    save_fl_model_weights
from decentralized_smart_grid_ml.handlers.participant_handler import ParticipantHandler
from decentralized_smart_grid_ml.utils.bcai_logging import create_logger
from decentralized_smart_grid_ml.utils.config import BLOCKCHAIN_ADDRESS, ANNOUNCEMENT_JSON_PATH, \
    get_addresses_contracts, PROJECT_ABSOLUTE_PATH

logger = create_logger(__name__)


class FakeFederatedLocalTrainer(FederatedLocalTrainer):
    """ This class is responsible for the creation of fake weights for the
    local participant's model """

    def fit_local_model(self, path_file_created):
        if path_file_created is not None:
            # try to load the aggregated new baseline model and start the local training
            round_baseline_model = Path(path_file_created).stem[-1]
            try:
                if int(round_baseline_model) == self.current_round:
                    aggregated_weights = load_fl_model_weights(path_file_created)
                    fake_weights = []
                    for weights in aggregated_weights:
                        fake_weights.append(rand(*weights.shape))
                    self.local_model.set_weights(fake_weights)
                else:
                    logger.warning(
                        "The path %s does not correspond to the current round (%d), Skipping...",
                        path_file_created, self.current_round
                    )
            except ValueError:
                logger.warning(
                    "Malformed path %s, Skipping...",
                    path_file_created
                )
                return self.is_finished
        else:
            # first round: the baseline model is in global_model_path
            aggregated_weights = self.local_model.get_weights()
            fake_weights = []
            for weights in aggregated_weights:
                fake_weights.append(rand(*weights.shape))
            self.local_model.set_weights(fake_weights)
        local_model_weights_path = os.path.join(
            self.local_model_weights_path,
            "weights_round_" + str(self.current_round) + ".json"
        )
        output_folder = Path(self.local_model_weights_path)
        output_folder.mkdir(parents=True, exist_ok=True)
        self.rounds2history[self.current_round] = None
        logger.info("Participant %s: end FL round %s", self.participant_id, self.current_round)
        self.current_round += 1
        save_fl_model_weights(self.local_model, local_model_weights_path)
        self.is_finished = self.current_round == self.announcement_config.fl_rounds
        return self.is_finished


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
    parser.add_argument(
        '--use_fake_weights',
        dest='use_fake_weights',
        action='store_true',
        help="Flag used to indicates if you want to use fake weights",
        default=False
    )

    args = parser.parse_args()
    logger.info("Starting participant script")

    announcement_contract_address, dex_contract_address = get_addresses_contracts(args.contract_info_path)

    # Client instance to interact with the blockchain
    web3 = Web3(HTTPProvider(BLOCKCHAIN_ADDRESS))
    logger.info("Connected to the blockchain %s", BLOCKCHAIN_ADDRESS)

    with open(ANNOUNCEMENT_JSON_PATH) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions

    # Fetch deployed contract reference
    contract = web3.eth.contract(address=announcement_contract_address, abi=contract_abi)
    logger.info("Fetched contract %s", announcement_contract_address)

    # automatically takes the idx + 1address
    participant_address = web3.eth.accounts[args.participant_id + 1]

    # subscribe in the task
    contract.functions.subscribe().transact({'from': participant_address})

    participant_id = contract.functions.getParticipantId().call({'from': participant_address})
    logger.info("The id of the participant is %s", participant_id)

    # extract the Announcement information from the smart contract
    announcement_configuration = AnnouncementConfiguration.retrieve_announcement_configuration(
        participant_address, contract
    )

    participant_directory_path = os.path.join(
        PROJECT_ABSOLUTE_PATH + "/data_sample/",
        announcement_configuration.task_name,
        "participants",
        "participant_" + str(participant_id)
    )

    local_dataset_path = os.path.join(
        participant_directory_path,
        announcement_configuration.task_name + "_" + str(participant_id) + ".csv"
    )

    maximum_number_participants = contract.functions.maxNumberParticipant().call({"from": participant_address})
    isStarted = False

    while not isStarted:
        number_participants = contract.functions.currentNumberParticipant().call({"from": participant_address})
        if number_participants != maximum_number_participants:
            logger.info("We need to wait that other participants subscribe to the task")
            time.sleep(2)
        else:
            isStarted = True

    time.sleep(2)
    logger.info("Starting participant federated learning")

    if args.use_fake_weights:
        federated_local_trainer = FakeFederatedLocalTrainer(
            participant_id,
            announcement_configuration,
            local_dataset_path,
            participant_directory_path
        )
    else:
        federated_local_trainer = FederatedLocalTrainer(
            participant_id,
            announcement_configuration,
            local_dataset_path,
            participant_directory_path
        )

    federated_local_trainer.fit_local_model(None)

    participant_handler = ParticipantHandler(federated_local_trainer)
    participant_observer = Observer()
    participant_observer.schedule(participant_handler, args.validator_directory_path, recursive=True)
    # start the observer
    logger.info("Starting the observer for the participant %s", participant_id)
    participant_observer.start()
    try:
        while not federated_local_trainer.is_finished:
            time.sleep(1)
    except KeyboardInterrupt as e:
        # stop and join the observer
        participant_observer.stop()
        participant_observer.join()
        logger.exception(e)
        logger.error("The participant %s did not completed his work", participant_id)
        sys.exit(-1)

    statistics_output_path = os.path.join(
        participant_directory_path,
        "statistics.json"
    )
    federated_local_trainer.write_statistics(statistics_output_path)

    logger.info("The participant %s terminated his work with success", participant_id)
    sys.exit(0)
