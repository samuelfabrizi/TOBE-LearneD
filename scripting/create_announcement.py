"""
This script permits the automatic initialization of an Announcement smart contract
"""
import argparse
import json
import sys
import time

import pandas as pd
from web3 import Web3, HTTPProvider
from tensorflow.keras.experimental import LinearModel
from tensorflow.keras import layers, models

from decentralized_smart_grid_ml.contract_interactions.announcement_configuration import AnnouncementConfiguration
from decentralized_smart_grid_ml.federated_learning.models_reader_writer import save_fl_model, \
    save_fl_model_config, save_fl_model_weights
from decentralized_smart_grid_ml.utils.bcai_logging import create_logger
from decentralized_smart_grid_ml.utils.config import BLOCKCHAIN_ADDRESS, ANNOUNCEMENT_JSON_PATH, \
    get_addresses_contracts, DEX_JSON_PATH, TOKEN_JSON_PATH

logger = create_logger(__name__)


def create_model(n_classes):
    # create a simple linear model as baseline
    #model = LinearModel(activation="sigmoid")
    #model.compile(optimizer="sgd", loss="mse", metrics="accuracy")
    #logger.info("Evaluation of baseline model %s", model.evaluate(x_test, y_test))
    # create a model for the appliance classification
    model = models.Sequential()
    model.add(layers.Dense(128, activation="relu"))
    model.add(layers.Dense(32, activation="relu"))
    model.add(layers.Dense(len(y_test[0]), activation="softmax"))
    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model


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
        '--task_config_path',
        dest='task_config_path',
        metavar='task_config_path',
        type=str,
        help="File path to the announcement's configuration file",
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
        '--n_tokens_at_stake',
        dest='n_tokens_at_stake',
        metavar='n_tokens_at_stake',
        type=int,
        help='The number of tokens at stake',
        required=True
    )
    parser.add_argument(
        '--max_number_participants',
        dest='max_number_participants',
        metavar='max_number_participants',
        type=int,
        help='The maximum number of participants admitted in the task',
        required=True
    )

    parser.add_argument(
        '--percentage_reward_validator',
        dest='percentage_reward_validator',
        metavar='percentage_reward_validator',
        type=int,
        help='The percentage of tokens to assign to the validator',
        required=True
    )
    args = parser.parse_args()
    logger.info("Starting script to initialize an announcement")

    announcement_contract_address, dex_contract_address = get_addresses_contracts(args.contract_info_path)
    announcement_config = AnnouncementConfiguration.read_json_config(args.task_config_path)

    # load test set
    test_set = pd.read_csv(args.test_set_path)
    logger.info("Dataset loaded from %s", args.test_set_path)

    x_test = test_set[announcement_config.features_names["features"]].values
    y_test = test_set[announcement_config.features_names["labels"]].values

    model = create_model(n_classes=len(y_test[0]))
    model.evaluate(x_test, y_test)

    # save the model's artifact
    save_fl_model(model, announcement_config.baseline_model_artifact)
    # save the model's config
    save_fl_model_config(model, announcement_config.baseline_model_config)
    # save the model's weights
    save_fl_model_weights(model, announcement_config.baseline_model_weights)

    # Client instance to interact with the blockchain
    web3 = Web3(HTTPProvider(BLOCKCHAIN_ADDRESS))
    logger.info("Connected to the blockchain %s", BLOCKCHAIN_ADDRESS)

    with open(ANNOUNCEMENT_JSON_PATH) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions

    with open(DEX_JSON_PATH) as file:
        dex_contract_json = json.load(file)  # load contract info as JSON
        dex_contract_abi = dex_contract_json['abi']  # fetch contract's abi - necessary to call its functions

    # Fetch deployed Announcement contract reference
    announcement_contract = web3.eth.contract(address=announcement_contract_address, abi=contract_abi)
    logger.info("Fetched announcement contract from %s", announcement_contract_address)

    # Fetch deployed GreenDEX contract reference
    dex_contract = web3.eth.contract(address=dex_contract_address, abi=dex_contract_abi)
    logger.info("Fetched GreenDEX contract from %s", dex_contract_address)

    # automatically takes the first address
    manufacturer_address = web3.eth.accounts[0]

    dex_contract.functions.buy().transact({
        'from': manufacturer_address,
        'value': args.n_tokens_at_stake
    })

    # Initialized the announcement
    announcement_contract.functions.initialize(
        args.task_config_path,              # path to the configuration file of the task
        args.max_number_participants,       # maximum number of participants,
        args.n_tokens_at_stake,             # number of tokens at stake
        args.percentage_reward_validator,   # percentage of tokens to assign to the validator
        web3.eth.accounts[5]                # validator address
    ).transact({'from': manufacturer_address})
    logger.info("The Announcement smart contract has been correctly initialized")

    token_contract_address = dex_contract.functions.greenToken().call({'from': manufacturer_address})

    with open(TOKEN_JSON_PATH) as file:
        token_contract_json = json.load(file)  # load contract info as JSON
        token_contract_abi = token_contract_json['abi']  # fetch contract's abi

    # Fetch deployed GreenToken contract reference
    dex_contract = web3.eth.contract(address=token_contract_address, abi=token_contract_abi)
    logger.info("Fetched GreenToken contract from %s", token_contract_address)

    # transfer of the tokens (reward) from the manufacturer to the announcement
    dex_contract.functions.transfer(
        announcement_contract_address,
        args.n_tokens_at_stake
    ).transact({'from': manufacturer_address})
    validator_reward = int(int(args.n_tokens_at_stake) * int(args.percentage_reward_validator) / 100)
    logger.info("The tokens' transfer has been correctly carried out")
    logger.info("Total number of tokens:  %s", args.n_tokens_at_stake)
    logger.info("Total reward for the validator: %s", validator_reward)
    logger.info("Total reward for the participants: %s", int(args.n_tokens_at_stake) - validator_reward)

    is_finished = False

    try:
        while not is_finished:
            if announcement_contract.functions.isFinished().call({'from': manufacturer_address}):
                is_finished = True
            else:
                logger.debug("Waiting the end of the task")
                time.sleep(5)
    except KeyboardInterrupt as e:
        logger.exception(e)
        logger.error("The manufacturer did not completed his work")
        sys.exit(-1)
    logger.info("The task is finished")
    announcement_contract.functions.assignRewards().transact({'from': manufacturer_address})
    logger.info("The rewards have been assigned")
    sys.exit(0)
