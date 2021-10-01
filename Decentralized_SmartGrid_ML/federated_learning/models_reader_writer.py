import json

import numpy as np
from tensorflow.python.keras.models import load_model, model_from_json

from Decentralized_SmartGrid_ML.utils.logging import create_logger

logger = create_logger(__name__)


def save_fl_model(model, model_path):
    model.save(model_path)
    logger.info("Model saved in directory %s", model_path)


def load_fl_model(model_path):
    model = load_model(model_path)
    logger.info("Load model from  %s", model_path)
    return model


def save_fl_model_config(model, model_path):
    with open(model_path, "w") as file_write:
        model_json = json.loads(model.to_json())
        json.dump(model_json, file_write, indent=1)
    logger.info("Model's config saved in %s", model_path)


def load_fl_model_config(model_path):
    with open(model_path, "r") as file_read:
        model_json = json.dumps(json.load(file_read))
    logger.info("Loaded model's config from  %s", model_path)
    return model_from_json(model_json)


def save_fl_model_weights(model, model_weights_path):
    weights_model = model.get_weights()
    lists_weights_model = [layer_weights.tolist() for layer_weights in weights_model]
    with open(model_weights_path, "w") as file_write:
        json.dump(lists_weights_model, file_write)
    logger.info("Model's weights saved in %s", model_weights_path)


def load_fl_model_weights(model_weights_path):
    with open(model_weights_path, "r") as file_read:
        model_weights = json.load(file_read)
    logger.info("Loaded model's weights from %s", model_weights_path)
    loaded_model_weights = [np.array(layer_weights) for layer_weights in model_weights]
    return loaded_model_weights

