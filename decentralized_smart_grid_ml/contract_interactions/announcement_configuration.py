"""
This module contains the functions used to interact with the Announcement Smart Contract
"""
import json

from decentralized_smart_grid_ml.utils.bcai_logging import create_logger

logger = create_logger(__name__)


class AnnouncementConfiguration:
    """
    This class represents an Announcement
    """

    def __init__(self, task_name, task_description, baseline_model_artifact,
                 baseline_model_weights, baseline_model_config, features_names,
                 fl_rounds, epochs):
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
        """
        self.task_name = task_name
        self.task_description = task_description
        self.baseline_model_artifact = baseline_model_artifact
        self.baseline_model_weights = baseline_model_weights
        self.baseline_model_config = baseline_model_config
        self.features_names = features_names
        self.fl_rounds = fl_rounds
        self.epochs = epochs

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
        logger.info("Configuration file path %s extract with success", config_task_path)
        with open(config_task_path, "r") as file_read:
            json_config_task = json.load(file_read)
        announcement_config = cls(
            json_config_task["task_name"],
            json_config_task["task_description"],
            json_config_task["baseline_model_artifact"],
            json_config_task["baseline_model_weights"],
            json_config_task["baseline_model_config"],
            json_config_task["features_names"],
            json_config_task["fl_rounds"],
            json_config_task["epochs"]
        )
        return announcement_config

    @classmethod
    def read_json_config(cls, config_path):
        """
        Reads the json that contains the Announcement's attributes
        :param config_path: file path to the configuration file
        :return: instance of AnnouncementConfiguration class
        """
        with open(config_path, "r") as file_read:
            json_config_task = json.load(file_read)
        announcement_config = cls(
            json_config_task["task_name"],
            json_config_task["task_description"],
            json_config_task["baseline_model_artifact"],
            json_config_task["baseline_model_weights"],
            json_config_task["baseline_model_config"],
            json_config_task["features_names"],
            json_config_task["fl_rounds"],
            json_config_task["epochs"]
        )
        return announcement_config
