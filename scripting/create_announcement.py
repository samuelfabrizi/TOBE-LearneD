"""
This script permits the automatic initialization of an Announcement smart contract
"""
import argparse
import json

import pandas as pd
from web3 import Web3, HTTPProvider
from tensorflow.keras.experimental import LinearModel

from decentralized_smart_grid_ml.federated_learning.models_reader_writer import save_fl_model, save_fl_model_config, \
    save_fl_model_weights
from decentralized_smart_grid_ml.utils.bcai_logging import create_logger
from decentralized_smart_grid_ml.utils.config import BLOCKCHAIN_ADDRESS, ANNOUNCEMENT_JSON_PATH

logger = create_logger(__name__)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

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
    args = parser.parse_args()
    logger.info("Starting script to initialize an announcement")

    # load test set
    test_set = pd.read_csv(args.test_set_path)
    logger.info("Dataset loaded from %s", args.test_set_path)

    # TODO: generalize this function to extract features and labels from the dataset
    x_test, y_test = test_set[["x1", "x2"]].values, test_set["y"].values
    # crate a simple linear model as baseline
    model = LinearModel(activation="sigmoid")
    model.compile(optimizer="sgd", loss="mse", metrics="accuracy")
    logger.info("Evaluation of baseline model %s", model.evaluate(x_test, y_test))

    # save the model's artifact
    save_fl_model(model, model_artifact)
    # save the model's config
    save_fl_model_config(model, model_config)
    # save the model's weights
    save_fl_model_weights(model, model_weights)

    # Client instance to interact with the blockchain
    web3 = Web3(HTTPProvider(BLOCKCHAIN_ADDRESS))
    logger.info("Connected to the blockchain %s", BLOCKCHAIN_ADDRESS)

    # Path to the compiled contract JSON file
    compiled_announcement_contract_path = ANNOUNCEMENT_JSON_PATH

    with open(compiled_announcement_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions

    # Fetch deployed contract reference
    contract = web3.eth.contract(address=args.announcement_contract_address, abi=contract_abi)
    logger.info("Fetched contract %s", args.announcement_contract_address)
    # automatically takes the first address
    manufacturer_address = web3.eth.accounts[0]
    # Call contract function (this is not persisted to the blockchain)
    contract.functions.initialize(
        task_name.encode('utf-8'),
        task_description.encode('utf-8'),
        task_deadline,
        model_artifact,
        model_config,
        model_weights,
        features_names,
        fl_rounds
    ).transact({'from': manufacturer_address})
    logger.info("The Announcement smart contract has been correctly initialized")
