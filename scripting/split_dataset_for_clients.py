"""
This script is a simple utility to split a given dataset so that it is possible to simulate the framework.
First of all, it extracts the test set for the validator. Then, it splits the remaining dataset according
to the number of clients.
"""
import argparse
import os
from pathlib import Path

from decentralized_smart_grid_ml.utils.bcai_logging import create_logger
from decentralized_smart_grid_ml.utils.fl_utility import split_dataset_validator_clients

logger = create_logger(__name__)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--dataset_path',
        dest='dataset_path',
        metavar='dataset_path',
        type=str,
        help='The file system path to the ML dataset to split',
        required=True
    )
    parser.add_argument(
        '--test_size',
        dest='test_size',
        metavar='test_size',
        type=float,
        help='The size of the test set, it has to be a float value between 0 and 1.0',
        default=0.2
    )
    parser.add_argument(
        '--n_clients',
        dest='n_clients',
        metavar='n_clients',
        type=int,
        help='The number of clients',
        required=True
    )
    parser.add_argument(
        '--ml_task_directory_path',
        dest='ml_task_directory_path',
        metavar='ml_task_directory_path',
        type=str,
        help='The directory path to the ML task',
        required=True
    )
    parser.add_argument(
        '--random_state',
        dest='random_state',
        metavar='random_state',
        type=int,
        help='Random state used to reproduce the split',
        default=None
    )
    parser.add_argument(
        '--shuffle',
        dest='shuffle',
        action='store_true',
        help='Flag used to indicates if you want to shuffle the dataset before the split',
        default=False,
    )

    args = parser.parse_args()
    logger.info("Starting dataset split script")
    dataset_test, datasets_clients = split_dataset_validator_clients(
        args.dataset_path,
        args.n_clients,
        args.test_size,
        random_state=args.random_state,
        shuffle=args.shuffle
    )
    dataset_name = Path(args.dataset_path).stem
    # store the clients' local datasets
    for idx_client, dataset_client in enumerate(datasets_clients):
        directory_client = os.path.join(
            args.ml_task_directory_path,
            "clients/client_" + str(idx_client)
        )
        Path(directory_client).mkdir(parents=True, exist_ok=True)
        dataset_client_path = os.path.join(
            directory_client,
            dataset_name + "_" + str(idx_client) + ".csv"
        )
        dataset_client.to_csv(str(dataset_client_path))
        logger.info("Dataset client %d saved in %s", idx_client, dataset_client_path)

    directory_validator = os.path.join(
        args.ml_task_directory_path,
        "validator"
    )
    Path(directory_validator).mkdir(parents=True, exist_ok=True)
    dataset_test_path = os.path.join(
        directory_validator,
        dataset_name + "_test.csv"
    )
    logger.info("Test set validator saved in %s", dataset_test_path)
    # store the validator's test datasets
    dataset_test.to_csv(str(dataset_test_path))
