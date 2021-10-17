"""
This module contains both functions and classes used to aggregate the local models' weights
in the global one
"""
import os
from pathlib import Path

import pandas as pd

from decentralized_smart_grid_ml.exceptions import NotValidParticipantsModelsError, \
    NotValidAlphaVectorError
from decentralized_smart_grid_ml.federated_learning.models_reader_writer import load_fl_model, \
    load_fl_model_weights, save_fl_model_weights
from decentralized_smart_grid_ml.utils.bcai_logging import create_logger

logger = create_logger(__name__)


def _index_in_list(a_list, index):
    return index < len(a_list)


def weighted_average_aggregation(models_weights, alpha):
    """
    Computes the weighted average of the participants' weights according to a given probability vector
    :param models_weights: weights of the participants' models
    :param alpha: probability vector for the weighted average
    :return: weighted average of weights
    """
    if sum(alpha) != 1:
        logger.error("The vector alpha is not valid %s", alpha)
        raise NotValidAlphaVectorError("Error in the alpha vector")
    if len(models_weights) != len(alpha):
        logger.error("The number of participants' weights (%d) and the vector alpha cardinality (%d) "
                     "does not correspond", len(models_weights), len(alpha))
        raise NotValidParticipantsModelsError("Error in the number of weights and/or alpha cardinality")
    logger.info("Start models' weights aggregation of %d participants", len(alpha))
    aggregated_weights = []
    for idx_participant, local_weights in enumerate(models_weights):
        for idx_layer, local_layer_weights in enumerate(local_weights):
            if not _index_in_list(aggregated_weights, idx_layer):
                aggregated_layer_weights = local_layer_weights * alpha[idx_participant]
                aggregated_weights.append(aggregated_layer_weights)
            else:
                if aggregated_weights[idx_layer].shape != local_layer_weights.shape:
                    logger.error(
                        "The shape of the layer %d, participant %d "
                        "does not correspond to the layer shape of the global model: %s != %s",
                        idx_layer,
                        idx_participant,
                        local_layer_weights.shape,
                        aggregated_weights[idx_layer].shape
                    )
                    raise NotValidParticipantsModelsError
                aggregated_weights[idx_layer] = \
                    aggregated_weights[idx_layer] + \
                    local_layer_weights * alpha[idx_participant]
            logger.debug("Update layer %d related to participant %d", idx_layer, idx_participant)
    logger.info("Finish models' weights aggregation of %d participants", len(alpha))
    return aggregated_weights


class Aggregator:
    """ This class is responsible for the participant models' aggregation """

    def __init__(self, participant_ids, n_fl_rounds,
                 global_model_path, test_set_path,
                 model_weights_new_round_path):
        """
        Initializes the aggregator
        :param participant_ids: participants' identifier
        :param n_fl_rounds: number of federated rounds
        :param global_model_path: directory path to the global baseline model
        :param test_set_path: file path to the test set
        :param model_weights_new_round_path: path to the directory that will contain the
            new model's weights (one for each round)
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
        self.model_weights_new_round_path = model_weights_new_round_path

    def _initialize_rounds2participants(self):
        """
        Initialize the rounds to participant information mapping
        :return:
        """
        for idx_round in range(self.n_fl_rounds):
            self.rounds2participants[idx_round] = {
                # TODO: takes a subset of the participant ids at each round
                "valid_participant_ids": self.participant_ids,
                "participant_weights": [],
                "participant_ids": []
            }

    def _local_training_is_completed(self, idx_round):
        """
        Checks if the local training of participants is completed
        :param idx_round: round that you want to check
        :return:    True if all the participants are published their model's weights
                    False otherwise
        """
        is_completed = \
            len(self.rounds2participants[idx_round]["participant_ids"]) \
            == \
            len(self.rounds2participants[idx_round]["valid_participant_ids"])
        return is_completed

    def add_participant_weights(self, path_file_created):
        """
        Adds the local weights (if valid) of a participant (if valid) in the current round
        :param path_file_created: file path to the local model's weights of the participant
        :return:    True if all the participant already publish their local model's weights
                    False otherwise
        """
        file_name_without_extension = Path(path_file_created).stem
        if file_name_without_extension.endswith("round_" + str(self.current_round)):
            directory = path_file_created.split("/")[-2]
            try:
                participant_id = int(directory[-1])
            except ValueError:
                logger.warning(
                    "Malformed path %s, Skipping...",
                    path_file_created
                )
                return False
            if \
                    participant_id in \
                    self.rounds2participants[self.current_round]["valid_participant_ids"] \
                    and participant_id not in \
                    self.rounds2participants[self.current_round]["participant_ids"]:
                self.rounds2participants[self.current_round]["participant_weights"].append(
                    load_fl_model_weights(path_file_created)
                )
                self.rounds2participants[self.current_round]["participant_ids"].append(
                    participant_id
                )
                is_completed = self._local_training_is_completed(self.current_round)
            else:
                logger.warning(
                    "The participant_id %s is not valid for the current round (%d), Skipping...",
                    participant_id,
                    self.current_round
                )
                is_completed = False
        else:
            logger.warning(
                "The path %s does not correspond to the current round (%d), Skipping...",
                path_file_created, self.current_round
            )
            is_completed = False
        return is_completed

    def _compute_participants_contribution(self, models_weights, participant_ids):
        """
        Computes the participants' contribution
        :param models_weights: participants models' weights (one for each participant in this round)
        :param participant_ids: participants' identifier (one for each participant in this round)
        :return: vector of the contribution
        """
        n_participants = len(participant_ids)
        # TODO: implement the mechanism to compute the actual participants' contribution
        alpha = [1.0 / n_participants for _ in range(n_participants)]
        logger.info(
            "Alpha vector for round %d is %s",
            self.current_round, alpha
        )
        return alpha

    def update_global_model(self):
        """
        Updates the global model and save both contribution and the evalution of the new model
        :return:
        """
        alpha = self._compute_participants_contribution(
            self.rounds2participants[self.current_round]["participant_weights"],
            self.rounds2participants[self.current_round]["participant_ids"]
        )
        # save the alpha vector (contribution) in the dictionary
        self.rounds2participants[self.current_round]["alpha"] = alpha
        # update the model
        global_weights = weighted_average_aggregation(
            self.rounds2participants[self.current_round]["participant_weights"],
            alpha
        )
        self.global_model.set_weights(global_weights)
        logger.debug("The global model has been updated with the new weights")
        evaluation_round = self.global_model.evaluate(self.x_test, self.y_test)
        logger.info(
            "Evaluation of the global model at round %d: %s",
            self.current_round,
            evaluation_round
        )
        self.rounds2participants[self.current_round]["evaluation"] = evaluation_round
        # next round can start
        self.current_round += 1
        if self.current_round == self.n_fl_rounds:
            baseline_file_name = os.path.join(
                self.model_weights_new_round_path,
                "validator_weights_final.json"
            )
        else:
            baseline_file_name = os.path.join(
                self.model_weights_new_round_path,
                "validator_weights_round_" + str(self.current_round) + ".json"
            )
        output_folder = Path(self.model_weights_new_round_path)
        output_folder.mkdir(parents=True, exist_ok=True)
        save_fl_model_weights(self.global_model, baseline_file_name)
