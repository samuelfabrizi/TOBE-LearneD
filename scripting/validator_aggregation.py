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
        '--n_participants',
        dest='n_participants',
        metavar='n_participants',
        type=int,
        help='The number of participants',
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
    #       validator and participants
    parser.add_argument(
        '--participant_weights_path',
        dest='participant_weights_path',
        metavar='participant_weights_path',
        type=str,
        help="The directory path that contains the sub-directories for the "
             "weights of the local trained participants' models",
        required=True
    )

    args = parser.parse_args()
    logger.info("Starting validator job")

    # TODO: change the participant_ids with the relative attribute in the Announcement
    participant_ids = list(range(args.n_participants))
    aggregator = Aggregator(
        participant_ids,
        args.n_fl_rounds,
        args.global_model_path,
        args.test_set_path,
        args.model_weights_new_round_path
    )
    aggregator_handler = ValidatorHandler(aggregator=aggregator)
    path = "."
    go_recursively = True

    validator_observer = Observer()
    validator_observer.schedule(aggregator_handler, args.participant_weights_path, recursive=True)
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
