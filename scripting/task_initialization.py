"""
This script is a simple utility to split a given dataset so that it is possible to simulate the framework.
First of all, it extracts the test set for the validator. Then, it splits the remaining dataset according
to the number of participants.
"""
import argparse
import os
from pathlib import Path

from decentralized_smart_grid_ml.utils.bcai_logging import create_logger
from decentralized_smart_grid_ml.utils.fl_utility import split_dataset_validator_participants

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
        '--n_participants',
        dest='n_participants',
        metavar='n_participants',
        type=int,
        help='The number of participants',
        required=True
    )
    parser.add_argument(
        '--ml_task_directory_path',
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

    dataset_test, datasets_participants = split_dataset_validator_participants(
        args.dataset_path,
        args.n_participants,
        args.test_size,
        random_state=args.random_state,
        shuffle=args.shuffle
    )
    dataset_name = Path(args.dataset_path).stem
    # store the participants' local datasets
    for idx_participant, dataset_participant in enumerate(datasets_participants):
        directory_participant = os.path.join(
            args.ml_task_directory_path,
            "participants/participant_" + str(idx_participant)
        )
        Path(directory_participant).mkdir(parents=True, exist_ok=True)
        dataset_participant_path = os.path.join(
            directory_participant,
            dataset_name + "_" + str(idx_participant) + ".csv"
        )
        dataset_participant.to_csv(str(dataset_participant_path))
        logger.info("Dataset participant %d saved in %s", idx_participant, dataset_participant_path)
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
