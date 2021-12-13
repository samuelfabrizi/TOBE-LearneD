"""
This module contains both functions and classes used to aggregate the local models' weights
in the global one
"""
import os
from pathlib import Path

import pandas as pd

from decentralized_smart_grid_ml.exceptions import NotValidParticipantsModelsError, \
    NotValidAlphaVectorError
from decentralized_smart_grid_ml.federated_learning.contributions_extractor import \
    ContributionsExtractorCreator
from decentralized_smart_grid_ml.federated_learning.models_reader_writer import load_fl_model, \
    load_fl_model_weights, save_fl_model_weights
from decentralized_smart_grid_ml.utils.bcai_logging import create_logger

logger = create_logger(__name__)


def _index_in_list(a_list, index):
    return index < len(a_list)


def weighted_average_aggregation(models_weights, alpha):
    """
    Computes the weighted average of the participants' weights
    according to a given probability vector
    :param models_weights: weights of the participants' models
    :param alpha: probability vector for the weighted average
    :return: weighted average of weights
    """
    if round(sum(alpha), 2) != 1:
        logger.error("The vector alpha is not valid %s", alpha)
        raise NotValidAlphaVectorError("Error in the alpha vector")
    if len(models_weights) != len(alpha):
        logger.error(
            "The number of participants' weights (%d) and the vector alpha cardinality (%d) "
            "does not correspond", len(models_weights), len(alpha)
        )
        raise NotValidParticipantsModelsError(
            "Error in the number of weights and/or alpha cardinality"
        )
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

    def __init__(self, participant_ids, announcement_config, validation_set_path,
                 test_set_path, model_weights_new_round_path):
        """
        Initializes the aggregator
        :param participant_ids: participants' identifier
        :param announcement_config: instance of AnnouncementConfiguration class
        :param validation_set_path: file path to the validation set
        :param test_set_path: file path to the test set
        :param model_weights_new_round_path: path to the directory that will contain the
            new model's weights (one for each round)
        """
        self.participant_ids = participant_ids
        self.announcement_config = announcement_config
        self.global_model = load_fl_model(announcement_config.baseline_model_artifact)
        test_set_df = pd.read_csv(test_set_path)
        validation_set_df = pd.read_csv(validation_set_path)
        self.x_val = validation_set_df[self.announcement_config.features_names["features"]].values
        self.y_val = validation_set_df[self.announcement_config.features_names["labels"]].values
        self.x_test = test_set_df[self.announcement_config.features_names["features"]].values
        self.y_test = test_set_df[self.announcement_config.features_names["labels"]].values
        self.rounds2participants = {}
        self._initialize_rounds2participants()
        self.current_round = 0
        self.model_weights_new_round_path = model_weights_new_round_path
        self.contribution_extractor = ContributionsExtractorCreator.factory_method(
            announcement_config.aggregation_method,
            self.global_model,
            self.x_val,
            self.y_val
        )
        self.is_finished = False

    def _initialize_rounds2participants(self):
        """
        Initialize the rounds to participant information mapping
        :return:
        """
        for idx_round in range(self.announcement_config.fl_rounds):
            self.rounds2participants[idx_round] = {
                # here the first key is not need for our purpose. In a future,
                # it will be possible to use it to take only a subset
                # of participants for each round
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

    def update_global_model(self):
        """
        Updates the global model and save both contribution and the evalution of the new model
        :return:
        """
        alpha = self.contribution_extractor.compute_contribution(
            self.rounds2participants[self.current_round]["participant_weights"],
        )
        logger.info(
            "Alpha vector for round %d is %s relative to participant ids %s",
            self.current_round, alpha,
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
            "Test set evaluation of the global model at round %d: %s",
            self.current_round,
            evaluation_round
        )
        self.rounds2participants[self.current_round]["evaluation"] = evaluation_round
        # next round can start
        self.current_round += 1
        if self.current_round == self.announcement_config.fl_rounds:
            baseline_file_name = os.path.join(
                self.model_weights_new_round_path,
                "validator_weights_final.json"
            )
            self.is_finished = True
        else:
            baseline_file_name = os.path.join(
                self.model_weights_new_round_path,
                "validator_weights_round_" + str(self.current_round) + ".json"
            )
        output_folder = Path(self.model_weights_new_round_path)
        output_folder.mkdir(parents=True, exist_ok=True)
        save_fl_model_weights(self.global_model, baseline_file_name)

    def get_participants_contributions(self):
        """
        Computes the participants' contribution considering the partial
        contribution obtained at each round
        :return: list of contributions (sum up to 1). The i-th contribution
            corresponds to the i-th participants (same positions of self.participant_ids)
        """
        participant_id2contributions_count = {}
        for participant_id in self.participant_ids:
            # here the key is the participant id while
            # the value is the sum of the participants' contribution
            participant_id2contributions_count[participant_id] = 0
        for idx_round in range(self.announcement_config.fl_rounds):
            fl_round_participants = self.rounds2participants[idx_round]["participant_ids"]
            contributions = self.rounds2participants[idx_round]["alpha"]
            for participant_id, contribution in zip(fl_round_participants, contributions):
                participant_id2contributions_count[participant_id] += contribution
        weighted_contributions = []
        for participant_id, total_contribution in \
                participant_id2contributions_count.items():
            weighted_contributions.append(round(
                total_contribution / self.announcement_config.fl_rounds, 2)
            )
        return weighted_contributions
