"""
This script is a simple example for the local federated training in the dummy ML task
"""

import argparse
import json
import os

import pandas as pd
from web3 import HTTPProvider, Web3

from decentralized_smart_grid_ml.federated_learning.models_reader_writer import load_fl_model, save_fl_model_weights
from decentralized_smart_grid_ml.utils.bcai_logging import create_logger

logger = create_logger(__name__)


# TODO: actually we need to take both epochs and batch size from a configuration file (or the Announcement SC)
EPOCHS = 5

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--client_id',
        dest='client_id',
        metavar='client_id',
        type=int,
        help='The client identifier',
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
        '--participant_address',
        dest='participant_address',
        metavar='participant_address',
        type=str,
        help='The address of the participant',
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
        '--n_fl_rounds',
        dest='n_fl_rounds',
        metavar='n_fl_rounds',
        type=int,
        help='Number of federated learning rounds',
        required=True
    )
    parser.add_argument(
        '--global_model_path',
        dest='global_model_path',
        metavar='global_model_path',
        type=str,
        help='The directory path to the global model',
        required=True
    )
    parser.add_argument(
        '--local_dataset_path',
        dest='local_dataset_path',
        metavar='local_dataset_path',
        type=str,
        help='The file path to local_dataset_path',
        required=True
    )
    # TODO: this argument has to be removed when we implemented the communication between
    #       validator and clients
    parser.add_argument(
        '--client_directory_path',
        dest='client_directory_path',
        metavar='client_directory_path',
        type=str,
        help='The path to the client directory',
        required=True
    )

    args = parser.parse_args()

    logger.info("Starting client %d federated learning", args.client_id)

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

    model_weights_path = os.path.join(
        args.client_directory_path,
        "weights_" + str(args.client_id) + ".json"
    )

    local_dataset = pd.read_csv(args.local_dataset_path)
    logger.info("Client %d: dataset loaded from %s", args.client_id, args.local_dataset_path)

    print(local_dataset.head())
    # TODO: generalize this function to extract features and labels from the dataset
    x, y = local_dataset[["x1", "x2"]].values, local_dataset["y"].values
    fl_rounds_completed = [None for _ in range(args.n_fl_rounds)]
    for idx_round in range(args.n_fl_rounds):
        # TODO: here we need to wait that the validator has published the global baseline model
        logger.info("Client %d: start FL round %d", args.client_id, idx_round)
        # read the initial global model at the start of the FL round
        local_model = load_fl_model(args.global_model_path)
        history = local_model.fit(x, y, epochs=EPOCHS, shuffle=True)
        # TODO: send the local model's weights at the end of the FL round
        save_fl_model_weights(local_model, model_weights_path)
        fl_rounds_completed[idx_round] = history
        logger.info("Client %d: end FL round %d", args.client_id, idx_round)
    for round_res in fl_rounds_completed:
        assert round_res is not None
