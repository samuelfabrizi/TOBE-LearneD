"""
This module contains a the functions used to aggregate the local models' weights
in the global one
"""
from pathlib import Path

import pandas as pd

from decentralized_smart_grid_ml.exceptions import NotValidClientsModelsError, \
    NotValidAlphaVectorError
from decentralized_smart_grid_ml.federated_learning.models_reader_writer import load_fl_model, \
    load_fl_model_weights
from decentralized_smart_grid_ml.utils.bcai_logging import create_logger

logger = create_logger(__name__)


def _index_in_list(a_list, index):
    return index < len(a_list)


def weighted_average_aggregation(models_weights, alpha):
    """
    Computes the weighted average of the clients' weights according to a given probability vector
    :param models_weights: weights of the clients' models
    :param alpha: probability vector for the weighted average
    :return: weighted average of weights
    """
    if sum(alpha) != 1:
        logger.error("The vector alpha is not valid %s", alpha)
        raise NotValidAlphaVectorError("Error in the alpha vector")
    if len(models_weights) != len(alpha):
        logger.error("The number of clients' weights (%d) and the vector alpha cardinality (%d) "
                     "does not correspond", len(models_weights), len(alpha))
        raise NotValidClientsModelsError("Error in the number of weights and/or alpha cardinality")
    logger.info("Start models' weights aggregation of %d clients", len(alpha))
    aggregated_weights = []
    for idx_client, local_weights in enumerate(models_weights):
        for idx_layer, local_layer_weights in enumerate(local_weights):
            if not _index_in_list(aggregated_weights, idx_layer):
                aggregated_layer_weights = local_layer_weights * alpha[idx_client]
                aggregated_weights.append(aggregated_layer_weights)
            else:
                if aggregated_weights[idx_layer].shape != local_layer_weights.shape:
                    logger.error(
                        "The shape of the layer %d, client %d "
                        "does not correspond to the layer shape of the global model: %s != %s",
                        idx_layer,
                        idx_client,
                        local_layer_weights.shape,
                        aggregated_weights[idx_layer].shape
                    )
                    raise NotValidClientsModelsError
                aggregated_weights[idx_layer] = \
                    aggregated_weights[idx_layer] + \
                    local_layer_weights * alpha[idx_client]
            logger.debug("Update layer %d related to client %d", idx_layer, idx_client)
    logger.info("Finish models' weights aggregation of %d clients", len(alpha))
    return aggregated_weights


class Aggregator:
    """ This class is responsible for the participant models' aggregation """

    def __init__(self, participant_ids, n_fl_rounds, global_model_path, test_set_path):
        """
        Initializes the aggregator
        :param participant_ids: participants' identifier
        :param n_fl_rounds: number of federated rounds
        :param global_model_path: directory path to the global baseline model
        :param test_set_path: file path to the test set
        """
        self.participant_ids = participant_ids
        self.n_fl_rounds = n_fl_rounds
        self.global_model = load_fl_model(global_model_path)
        test_set_df = pd.read_csv(test_set_path)
        # TODO: generalize this function to extract features and labels from the dataset
        self.x_test, self.y_test = test_set_df[["x1", "x2"]].values, test_set_df["y"].values
        self.rounds2participants = {}
        self._initialize_rounds2participants()
        self.current_round = 0

    def _initialize_rounds2participants(self):
        for idx_round in range(self.n_fl_rounds):
            self.rounds2participants[idx_round] = {
                # TODO: takes a subset of the client ids at each round
                "valid_participant_ids": self.participant_ids,
                "participant_weights": [],
                "participant_ids": []
            }

    def add_participant_weights(self, path_file_created):
        """
        Adds the local weights (if valid) of a participant (if valid) in the current round
        :param path_file_created: file path to the local model's weights of the client
        :return:
        """
        file_name_without_extension = Path(path_file_created).stem
        if file_name_without_extension.endswith("round_" + str(self.current_round)):
            directory = path_file_created.split("/")[-2]
            participant_id = int(directory[-1])
            if participant_id in \
                    self.rounds2participants[self.current_round]["valid_participant_ids"]:
                self.rounds2participants[self.current_round]["participant_weights"].append(
                    load_fl_model_weights(path_file_created)
                )
                self.rounds2participants[self.current_round]["participant_ids"].append(
                    participant_id
                )
            else:
                logger.warning(
                    "The participant_id %s is not valid for the current round (%d), Skipping...",
                    participant_id,
                    self.current_round
                )
        else:
            logger.warning(
                "The path %s does not correspond to the current round (%d), Skipping...",
                path_file_created, self.current_round
            )
