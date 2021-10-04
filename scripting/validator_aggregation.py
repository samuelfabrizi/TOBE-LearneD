"""
This script runs the Federate Learning life cycle of the validator
"""
import argparse
import os

from decentralized_smart_grid_ml.federated_learning.federated_aggregator import weighted_average_aggregation
from decentralized_smart_grid_ml.federated_learning.models_reader_writer import load_fl_model_weights
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

    path_clients_weights = []
    for idx_client in range(args.n_clients):
        client_path = os.path.join(
            args.client_weights_path,
            "client_" + str(idx_client),
            "weights_" + str(idx_client) + ".json"
        )
        # here we exploit the fact that the ids goes from 0 to n_clients-1
        path_clients_weights.append(client_path)

    # TODO: change the alpha vector with the real contributions
    alpha = [1.0 / args.n_clients for _ in range(args.n_clients)]

    for idx_round in range(args.n_fl_rounds):
        # TODO: here we need to wait that the validator has published the global baseline model
        logger.info("Start aggregation FL round %d", idx_round)
        # TODO: here we need to have the clients' identifier (maybe in the smart contract)
        clients_weights = []
        for idx_client in range(args.n_clients):
            clients_weights.append((load_fl_model_weights(path_clients_weights[idx_client])))
        global_weights = weighted_average_aggregation(clients_weights, alpha)
        # TODO: load the model, set the new weights and compute the metrics for the evaluation
        #       on the test set
        logger.info("End aggregation FL round %d", idx_round)