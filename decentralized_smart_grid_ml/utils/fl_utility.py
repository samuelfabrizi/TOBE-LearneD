"""
This module contains some utilities for the federated learning task
"""
import pathlib

import numpy as np
import pandas as pd
from sklearn.utils import shuffle as sk_shuffle

from decentralized_smart_grid_ml.exceptions import IncorrectExtensionFileError
from decentralized_smart_grid_ml.utils.bcai_logging import create_logger

logger = create_logger(__name__)


def split_dataset_validator_participants(dataset_path, n_participants, validation_size=0.15,
                                         test_size=0.2, random_state=None, shuffle=False,
                                         unbalanced=False):
    """
    Splits a given dataset in N datasets, one for each participant
    :param dataset_path: file path to the whole original dataset
    :param n_participants: number of participants
    :param random_state: random state used for reproducibility
    :param test_size: represents the proportion of the dataset to include in the test split
    :param validation_size: represents the proportion of the dataset to include in the test split
    :param shuffle: if it is True, the dataset is shuffled
    :param unbalanced: if it is true, the participants' dataset will be unbalanced
    :return: (dataset_test, dataset_validation, participants_dataset) where
            dataset_test is the validator's test split
            dataset_validation is the validator's validation split
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

    # get the number of examples in the validation split
    n_example_validation = int(len(df_dataset_participants) * validation_size)
    df_dataset_validation = df_dataset_participants[:n_example_validation]
    df_dataset_participants = df_dataset_participants[n_example_validation:]
    logger.info("The test split contains %d examples", len(df_dataset_test))

    if not unbalanced:
        participants_datasets = np.array_split(df_dataset_participants, n_participants)
    else:
        np.random.seed(random_state)
        participants_distribution = \
            np.random.dirichlet(np.ones(n_participants), 1).\
            flatten()
        participants_distribution = np.array(
            participants_distribution * len(df_dataset_participants),
            dtype=int
        )
        already_assigned_rows = 0
        participants_datasets = []
        for i, chunks in enumerate(participants_distribution):
            if i == n_participants - 1:
                participant_dataset = \
                    df_dataset_participants[already_assigned_rows:]
            else:
                participant_dataset = \
                    df_dataset_participants[already_assigned_rows:already_assigned_rows+chunks]
            participants_datasets.append(participant_dataset)
            already_assigned_rows += chunks
    participants_df_length = [len(participant_df) for participant_df in participants_datasets]
    assert sum(participants_df_length) == len(df_dataset_participants)
    logger.info("The dataset distribution is the following: %s", participants_df_length)
    return df_dataset_test, df_dataset_validation, participants_datasets
