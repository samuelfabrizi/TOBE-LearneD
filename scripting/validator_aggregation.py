"""
This script runs the Federate Learning life cycle of the validator
"""
import argparse
import time

from watchdog.observers import Observer

from decentralized_smart_grid_ml.federated_learning.federated_aggregator import Aggregator
from decentralized_smart_grid_ml.handlers.validator_handler import ValidatorHandler
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
        '--test_set_path',
        dest='test_set_path',
        metavar='test_set_path',
        type=str,
        help='The file path to the test set',
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
    parser.add_argument(
        '--model_weights_new_round_path',
        dest='model_weights_new_round_path',
        metavar='model_weights_new_round_path',
        type=str,
        help="The directory path to the model's weights for each round",
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
             "weights of the local trained clients' models",
        required=True
    )

    args = parser.parse_args()
    logger.info("Starting validator job")

    # TODO: change the client_ids with the relative attribute in the Announcement
    client_ids = list(range(args.n_clients))
    aggregator = Aggregator(
        client_ids,
        args.n_fl_rounds,
        args.global_model_path,
        args.test_set_path,
        args.model_weights_new_round_path
    )
    aggregator_handler = ValidatorHandler(aggregator=aggregator)
    path = "."
    go_recursively = True

    validator_observer = Observer()
    validator_observer.schedule(aggregator_handler, args.client_weights_path, recursive=True)
    # start the observer
    logger.info("Starting the observer for the validator")
    validator_observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # stop and join the observer
        validator_observer.stop()
        validator_observer.join()
