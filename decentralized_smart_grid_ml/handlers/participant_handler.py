"""
This module contains the Participant Handler class used to trigger the functions
used to train the local model when a new global model is available
"""
from watchdog.events import FileSystemEventHandler

from decentralized_smart_grid_ml.utils.bcai_logging import create_logger

logger = create_logger(__name__)


class ParticipantHandler(FileSystemEventHandler):
    """ This class is responsible to trigger Aggregator actions when a new file is created
    in a given path """

    def __init__(self, federated_local_trainer):
        """
        Initializes the handler
        :param federated_local_trainer: instance of FederatedLocalTrainer
        """
        self.federated_local_trainer = federated_local_trainer
        super().__init__()

    def on_created(self, event):
        """
        Triggers an update in the aggregator
        :param event: event generated
        :return:
        """
        logger.info("The file %s has been created", event.src_path)
        self.federated_local_trainer.fit_local_model(event.src_path)
