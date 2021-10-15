"""
This module contains some utilities for the federated learning task
"""
import pathlib

import pandas as pd
from sklearn.utils import shuffle as sk_shuffle

from decentralized_smart_grid_ml.exceptions import IncorrectExtensionFileError
from decentralized_smart_grid_ml.utils.bcai_logging import create_logger

logger = create_logger(__name__)


def split_dataset_validator_clients(dataset_path, n_clients, test_size=0.2,
                                    random_state=None, shuffle=False):
    """
    Splits a given dataset in N datasets, one for each client
    :param dataset_path: file path to the whole original dataset
    :param n_clients: number of clients
    :param random_state: random state used for reproducibility
    :param test_size: represents the proportion of the dataset to include in the test split
    :param shuffle: if it is True, the dataset is shuffled
    :return: (dataset_test, clients_dataset) where
            dataset_test is the validator's test split
            clients_dataset are n_clients dataset, one for each client
    """
    if pathlib.Path(dataset_path).suffix != ".csv":
        logger.error("The file path %s is not a csv file", dataset_path)
        raise IncorrectExtensionFileError("Error in the file extension, csv is required")
    if n_clients <= 0:
        logger.error("The number of clients provided is not valid: %d is not > 0", n_clients)
        raise ValueError("The number of clients must be a positive integer")
    if test_size <= 0:
        logger.error("The test size provided is not valid: %f is not > 0", test_size)
        raise ValueError("The test size must be a value in the range (0.0, 1.0)")
    df_dataset = pd.read_csv(dataset_path)
    if shuffle:
        df_dataset = sk_shuffle(df_dataset, random_state=random_state)
    # get the number of examples in the test split
    n_example_test = int(len(df_dataset) * test_size)
    df_dataset_test = df_dataset[:n_example_test]
    df_dataset_clients = df_dataset[n_example_test:]
    logger.info("The test split contains %d examples", len(df_dataset_test))
    n_samples = len(df_dataset_clients)
    chunk_size = int(n_samples / n_clients)
    clients_datasets = []
    for i in range(n_clients):
        if i == (n_clients - 1):
            clients_datasets.append(df_dataset_clients.iloc[i*chunk_size:])
        else:
            clients_datasets.append(df_dataset_clients.iloc[chunk_size*i:chunk_size*(i+1)])
    return df_dataset_test, clients_datasets
