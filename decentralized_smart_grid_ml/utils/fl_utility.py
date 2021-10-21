"""
This module contains some utilities for the federated learning task
"""
import pathlib

import pandas as pd
from sklearn.utils import shuffle as sk_shuffle

from decentralized_smart_grid_ml.exceptions import IncorrectExtensionFileError
from decentralized_smart_grid_ml.utils.bcai_logging import create_logger

logger = create_logger(__name__)


def split_dataset_validator_participants(dataset_path, n_participants, test_size=0.2,
                                    random_state=None, shuffle=False):
    """
    Splits a given dataset in N datasets, one for each participant
    :param dataset_path: file path to the whole original dataset
    :param n_participants: number of participants
    :param random_state: random state used for reproducibility
    :param test_size: represents the proportion of the dataset to include in the test split
    :param shuffle: if it is True, the dataset is shuffled
    :return: (dataset_test, participants_dataset) where
            dataset_test is the validator's test split
            participants_dataset are n_participants dataset, one for each participant
    """
    if pathlib.Path(dataset_path).suffix != ".csv":
        logger.error("The file path %s is not a csv file", dataset_path)
        raise IncorrectExtensionFileError("Error in the file extension, csv is required")
    if n_participants <= 0:
        logger.error(
            "The number of participants provided is not valid: %d is not > 0",
            n_participants
        )
        raise ValueError("The number of participants must be a positive integer")
    if test_size <= 0:
        logger.error("The test size provided is not valid: %f is not > 0", test_size)
        raise ValueError("The test size must be a value in the range (0.0, 1.0)")
    df_dataset = pd.read_csv(dataset_path)
    if shuffle:
        df_dataset = sk_shuffle(df_dataset, random_state=random_state)
    # get the number of examples in the test split
    n_example_test = int(len(df_dataset) * test_size)
    df_dataset_test = df_dataset[:n_example_test]
    df_dataset_participants = df_dataset[n_example_test:]
    logger.info("The test split contains %d examples", len(df_dataset_test))
    n_samples = len(df_dataset_participants)
    chunk_size = int(n_samples / n_participants)
    participants_datasets = []
    for i in range(n_participants):
        if i == (n_participants - 1):
            participants_datasets.append(df_dataset_participants.iloc[i*chunk_size:])
        else:
            participants_datasets.append(
                df_dataset_participants.iloc[chunk_size*i:chunk_size*(i+1)]
            )
    return df_dataset_test, participants_datasets
