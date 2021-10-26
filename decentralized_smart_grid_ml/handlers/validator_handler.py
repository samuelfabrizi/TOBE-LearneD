"""
This module contains the Validator Handler class used to trigger the functions
used to compute the aggregated model at each round
"""
from watchdog.events import FileSystemEventHandler

from decentralized_smart_grid_ml.utils.bcai_logging import create_logger

logger = create_logger(__name__)


class ValidatorHandler(FileSystemEventHandler):
    """ This class is responsible to trigger Aggregator actions when a new file is created
    in a given path """

    def __init__(self, aggregator):
        """
        Initializes the handler
        :param aggregator: instance of Aggregator
        """
        self.aggregator = aggregator
        super().__init__()

    def on_created(self, event):
        """
        Triggers an update in the aggregator
        :param event: event generated
        :return:
        """
        if not self.aggregator.is_finished:
            logger.info("The file %s has been created", event.src_path)
            round_is_completed = self.aggregator.add_participant_weights(event.src_path)
            if round_is_completed:
                self.aggregator.update_global_model()
