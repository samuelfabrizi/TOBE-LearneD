"""
This script runs the Federate Learning life cycle of the validator
"""
import argparse

from decentralized_smart_grid_ml.utils.bcai_logging import create_logger

logger = create_logger(__name__)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
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
        '--n_clients',
        dest='n_clients',
        metavar='n_clients',
        type=int,
        help='The number of clients',
        required=True
    )
    # TODO: this argument has to be removed when we implemented the communication between
    #       validator and clients
    parser.add_argument(
        '--client_weights_path',
        dest='client_weights_path',
        metavar='client_weights_path',
        type=str,
        help="The directory path that contains the sub-directories for the "
             "weights of the clients' models",
        required=True
    )

    args = parser.parse_args()
    logger.info("Starting validator %d federated learning")