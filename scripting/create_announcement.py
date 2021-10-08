import argparse
import json

from web3 import Web3, HTTPProvider

from decentralized_smart_grid_ml.utils.bcai_logging import create_logger

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
        '--manufacturer_address',
        dest='manufacturer_address',
        metavar='manufacturer_address',
        type=str,
        help='The address of the manufacturer',
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
        '--task_deadline',
        dest='task_deadline',
        metavar='task_deadline',
        type=int,
        help='The deadline of the task',
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
        '--features_names',
        dest='features_names',
        metavar='features_names',
        type=str,
        help="The file path to features names",
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
    args = parser.parse_args()
    logger.info("Starting script to initialize an announcement")

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
    # Call contract function (this is not persisted to the blockchain)
    contract.functions.initialize(
        args.task_name.encode('utf-8'),
        args.task_description.encode('utf-8'),
        args.task_deadline,
        args.model_artifact.encode('utf-8'),
        args.model_config.encode('utf-8'),
        args.model_weights.encode('utf-8'),
        args.features_names.encode('utf-8'),
        args.fl_rounds
    ).transact({'from': args.manufacturer_address})
    logger.info("The Announcement smart contract has been correctly initialized")
