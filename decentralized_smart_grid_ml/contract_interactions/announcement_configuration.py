"""
This module contains the functions used to interact with the Announcement Smart Contract
"""
import json

from decentralized_smart_grid_ml.exceptions import MalformedConfigurationJson
from decentralized_smart_grid_ml.utils.bcai_logging import create_logger

logger = create_logger(__name__)


class AnnouncementConfiguration:
    """
    This class represents an Announcement
    """

    def __init__(self, task_name, task_description, baseline_model_artifact,
                 baseline_model_weights, baseline_model_config, features_names,
                 fl_rounds, epochs, batch_size, aggregation_method):
        """
        Constructor
        :param task_name: name of the task
        :param task_description: description of the task
        :param baseline_model_artifact: path to the baseline model's artifact
        :param baseline_model_weights: path to the baseline model's weights
        :param baseline_model_config: path to the baseline model's config
        :param features_names: features name of the dataset (features and labels)
        :param fl_rounds: number of federated rounds
        :param epochs: number of epochs
        :param batch_size: batch size
        :param aggregation_method: method used to aggregate the participants' models
        """
        self.task_name = task_name
        self.task_description = task_description
        self.baseline_model_artifact = baseline_model_artifact
        self.baseline_model_weights = baseline_model_weights
        self.baseline_model_config = baseline_model_config
        self.features_names = features_names
        self.fl_rounds = fl_rounds
        self.epochs = epochs
        self.batch_size = batch_size
        self.aggregation_method = aggregation_method

    @classmethod
    def retrieve_announcement_configuration(cls, user_address, contract_instance):
        """
        Retrieves a python class that represents an Announcement
        :param user_address: ethereum address of the user
        :param contract_instance: instance of the Announcement smart contract
        :return: instance of AnnouncementConfiguration class
            that represents the Announcement SC required
        """
        config_task_path = contract_instance.functions.taskConfiguration().call(
            {"from": user_address}
        )
        logger.info("Configuration file path %s extract with success from the blockchain",
                    config_task_path)
        return AnnouncementConfiguration.read_json_config(config_task_path)

    @classmethod
    def read_json_config(cls, config_path):
        """
        Reads the json that contains the Announcement's attributes
        :param config_path: file path to the configuration file
        :return: instance of AnnouncementConfiguration class
        """
        with open(config_path, "r") as file_read:
            json_config_task = json.load(file_read)
        try:
            announcement_config = cls(
                json_config_task["task_name"],
                json_config_task["task_description"],
                json_config_task["baseline_model_artifact"],
                json_config_task["baseline_model_weights"],
                json_config_task["baseline_model_config"],
                json_config_task["features_names"],
                json_config_task["fl_rounds"],
                json_config_task["epochs"],
                json_config_task["batch_size"],
                json_config_task["aggregation_method"]
            )
        except KeyError as key_error:
            logger.error("One or more key are missing in the "
                         "json configuration file %s", config_path)
            raise MalformedConfigurationJson from key_error
        return announcement_config
