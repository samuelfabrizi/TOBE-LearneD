"""
This script is a simple example for the local federated training in the dummy ML task
"""

import argparse

import pandas as pd

from decentralized_smart_grid_ml.federated_learning.models_reader_writer import load_fl_model
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

    args = parser.parse_args()
    logger.info("Starting client %d federated learning", args.client_id)

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
        logger.debug(
            "Client %d, round %d, weights: %s",
            args.client_id,
            idx_round,
            local_model.get_weights()
        )
        fl_rounds_completed[idx_round] = history
        logger.info("Client %d: end FL round %d", args.client_id, idx_round)

