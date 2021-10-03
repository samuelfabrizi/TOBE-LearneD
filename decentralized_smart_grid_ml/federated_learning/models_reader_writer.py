"""
Utility to save and load models' config and weights
"""
import json
import pathlib

import numpy as np
from tensorflow.keras import models as tf_models

from decentralized_smart_grid_ml.exceptions import IncorrectExtensionFileError
from decentralized_smart_grid_ml.utils.logging import create_logger

logger = create_logger(__name__)


def save_fl_model(model, model_path):
    """
    Saves the whole model in a given path
    :param model: model to save
    :param model_path: directory path in which the model will be saved
    :return:
    """
    model.save(model_path)
    logger.info("Model saved in directory %s", model_path)


def load_fl_model(model_path):
    """
    Loads a whole model from given path
    :param model_path: directory path in which the model has been saved
    :return: loaded model
    """
    model = tf_models.load_model(model_path)
    logger.info("Load model from  %s", model_path)
    return model


def save_fl_model_config(model, model_path):
    """
    Saves the configuration of the model in a json file
    :param model: model that ccontains the config to save
    :param model_path: file path in which the model's config will be saved
    :return:
    """
    if pathlib.Path(model_path).suffix != ".json":
        logger.error("The file path %s is not a json file", model_path)
        raise IncorrectExtensionFileError()
    with open(model_path, "w") as file_write:
        model_json = json.loads(model.to_json())
        json.dump(model_json, file_write, indent=1)
    logger.info("Model's config saved in %s", model_path)


def load_fl_model_config(model_path):
    """
    Loads a model's config
    :param model_path: file path in which the model's config has been saved
    :return: loaded model's config
    """
    if pathlib.Path(model_path).suffix != ".json":
        logger.error("The file path %s is not a json file", model_path)
        raise IncorrectExtensionFileError()
    with open(model_path, "r") as file_read:
        model_json = json.dumps(json.load(file_read))
    logger.info("Loaded model's config from  %s", model_path)
    model_json = tf_models.model_from_json(model_json)
    return model_json


def save_fl_model_weights(model, model_weights_path):
    """
    Saves the model's weights in a json file
    :param model: model that contains the weights to save
    :param model_weights_path: file path in which the model's weights will be saved
    :return:
    """
    if pathlib.Path(model_weights_path).suffix != ".json":
        logger.error("The file path %s is not a json file", model_weights_path)
        raise IncorrectExtensionFileError()
    weights_model = model.get_weights()
    lists_weights_model = [layer_weights.tolist() for layer_weights in weights_model]
    with open(model_weights_path, "w") as file_write:
        json.dump(lists_weights_model, file_write, indent=1)
    logger.info("Model's weights saved in %s", model_weights_path)


def load_fl_model_weights(model_weights_path):
    """
    Loads the model's weights
    :param model_weights_path: file path in which the model's weights has been saved
    :return: loaded model's weights
    """
    if pathlib.Path(model_weights_path).suffix != ".json":
        logger.error("The file path %s is not a json file", model_weights_path)
        raise IncorrectExtensionFileError()
    with open(model_weights_path, "r") as file_read:
        model_weights = json.load(file_read)
    logger.info("Loaded model's weights from %s", model_weights_path)
    loaded_model_weights = [np.array(layer_weights) for layer_weights in model_weights]
    return loaded_model_weights
