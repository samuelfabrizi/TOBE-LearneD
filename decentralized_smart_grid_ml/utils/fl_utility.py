"""
This module contains some utilities for the federated learning task
"""
import pathlib

import pandas as pd
from sklearn.utils import shuffle as sk_shuffle

from decentralized_smart_grid_ml.exceptions import IncorrectExtensionFileError
from decentralized_smart_grid_ml.utils.bcai_logging import create_logger

logger = create_logger(__name__)


def split_dataset_for_clients(dataset_path, n_clients, random_state=None, shuffle=False):
    """
    Splits a given dataset in N datasets, one for each client
    :param dataset_path: file path to the whole original dataset
    :param n_clients: number of clients
    :param random_state: random state used for reproducibility
    :param shuffle: if it is True, the dataset is shuffled
    :return: n_clients dataset, one for each client
    """
    if pathlib.Path(dataset_path).suffix != ".csv":
        logger.error("The file path %s is not a csv file", dataset_path)
        raise IncorrectExtensionFileError("Error in the file extension, csv is required")
    if n_clients <= 0:
        logger.error("The number of clients provided is not valid: %d is not > 0", n_clients)
        raise ValueError("The number of clients must be a positive integer")
    df = pd.read_csv(dataset_path, )
    if shuffle:
        df = sk_shuffle(df, random_state=random_state)
    n_samples = len(df)
    chunk_size = int(n_samples / n_clients)
    clients_datasets = []
    for i in range(n_clients):
        if i == (n_clients - 1):
            clients_datasets.append(df.iloc[i*chunk_size:])
        else:
            clients_datasets.append(df.iloc[chunk_size*i:chunk_size*(i+1)])
    return clients_datasets
