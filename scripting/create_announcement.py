"""
This script permits the automatic initialization of an Announcement smart contract
"""
import argparse
import json

import pandas as pd
from web3 import Web3, HTTPProvider
from tensorflow.keras.experimental import LinearModel

from decentralized_smart_grid_ml.contract_interactions.announcement_configuration import AnnouncementConfiguration
from decentralized_smart_grid_ml.federated_learning.models_reader_writer import save_fl_model, \
    save_fl_model_config, save_fl_model_weights
from decentralized_smart_grid_ml.utils.bcai_logging import create_logger
from decentralized_smart_grid_ml.utils.config import BLOCKCHAIN_ADDRESS, ANNOUNCEMENT_JSON_PATH

logger = create_logger(__name__)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--announcement_contract_address',
        dest='announcement_contract_address',
        metavar='announcement_contract_address',
        type=str,
        help='The address of the announcement contract',
        required=True
    )
    parser.add_argument(
        '--task_name',
        dest='task_name',
        metavar='task_name',
        type=str,
        help='The name of the task',
        required=True
    )
    parser.add_argument(
        '--task_description',
        dest='task_description',
        metavar='task_description',
        type=str,
        help='The description of the task',
        required=True
    )
    parser.add_argument(
        '--model_artifact',
        dest='model_artifact',
        metavar='model_artifact',
        type=str,
        help='The directory path to the whole model (both config and weights)',
        required=True
    )
    parser.add_argument(
        '--model_config',
        dest='model_config',
        metavar='model_config',
        type=str,
        help="The file path to model's config",
        required=True
    )
    parser.add_argument(
        '--model_weights',
        dest='model_weights',
        metavar='model_weights',
        type=str,
        help="The file path to model's config",
        required=True
    )
    parser.add_argument(
        '--fl_rounds',
        dest='fl_rounds',
        metavar='fl_rounds',
        type=int,
        help='The number of federated rounds',
        required=True
    )
    parser.add_argument(
        '--epochs',
        dest='epochs',
        metavar='epochs',
        type=int,
        help='The number of epochs to train the local models',
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
    # create a simple linear model as baseline
    model = LinearModel(activation="sigmoid")
    model.compile(optimizer="sgd", loss="mse", metrics="accuracy")
    logger.info("Evaluation of baseline model %s", model.evaluate(x_test, y_test))

    # save the model's artifact
    save_fl_model(model, args.model_artifact)
    # save the model's config
    save_fl_model_config(model, args.model_config)
    # save the model's weights
    save_fl_model_weights(model, args.model_weights)

    # Client instance to interact with the blockchain
    web3 = Web3(HTTPProvider(BLOCKCHAIN_ADDRESS))
    logger.info("Connected to the blockchain %s", BLOCKCHAIN_ADDRESS)

    with open(ANNOUNCEMENT_JSON_PATH) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions

    # Fetch deployed contract reference
    contract = web3.eth.contract(address=args.announcement_contract_address, abi=contract_abi)
    logger.info("Fetched contract %s", args.announcement_contract_address)

    announcement_config = AnnouncementConfiguration(
        args.task_name,
        args.task_description,
        args.model_artifact,
        args.model_config,
        args.model_weights,
        # TODO: substitute with real feature names
        "features names",
        args.fl_rounds,
        args.epochs
    )

    # write the json config in the file system
    announcement_config.write_json_config(args.task_config_path)

    # automatically takes the first address
    manufacturer_address = web3.eth.accounts[0]
    # Call contract function (this is not persisted to the blockchain)
    contract.functions.initialize(
        args.task_config_path,
        8       # maximum number of participants
    ).transact({'from': manufacturer_address})
    logger.info("The Announcement smart contract has been correctly initialized")
