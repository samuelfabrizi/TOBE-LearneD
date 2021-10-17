"""
This module contains the class responsible for the training of the local participant's model
"""
import os
from pathlib import Path

import pandas as pd

from decentralized_smart_grid_ml.federated_learning.models_reader_writer import load_fl_model, \
    load_fl_model_weights, save_fl_model_weights
from decentralized_smart_grid_ml.utils.bcai_logging import create_logger

logger = create_logger(__name__)


class FederatedLocalTrainer:
    """ This class is responsible for the training of the local participant's model """

    def __init__(self, participant_id, n_fl_rounds, global_model_path,
                 train_set_path, epochs, local_model_weights_path):
        """
        Initialized the local trainer
        :param participant_id: id of the participant
        :param n_fl_rounds: number of federated rounds
        :param global_model_path: directory path to the global baseline model
        :param train_set_path: file path to the training set
        :param epochs: number of epochs
        :param local_model_weights_path: path to the directory that will contain the
            local model's weights(one for each round)
        """
        self.participant_id = participant_id
        self.n_fl_rounds = n_fl_rounds
        self.local_model = load_fl_model(global_model_path)
        train_set_df = pd.read_csv(train_set_path)
        # TODO: generalize this function to extract features and labels from the dataset
        self.x_train, self.y_train = train_set_df[["x1", "x2"]].values, train_set_df["y"].values
        self.epochs = epochs
        self.local_model_weights_path = local_model_weights_path
        self.rounds2history = {}
        self._initialize_rounds2history()
        self.current_round = 0
        self.is_finished = False

    def _initialize_rounds2history(self):
        """
        Initialize the rounds to history information mapping
        :return:
        """
        for idx_round in range(self.n_fl_rounds):
            self.rounds2history[idx_round] = None

    def fit_local_model(self, path_file_created):
        """
        Carries out the training of the local model for one round
        :param path_file_created:   file path to the aggregated model's weights
                                    for the current round or None if the participant
                                    has to fit the model for the first time
        :return:    True if the training of the last round is finished
                    False otherwise
        """
        history = None
        if path_file_created is not None:
            # try to load the aggregated new baseline model and start the local training
            round_baseline_model = Path(path_file_created).stem[-1]
            try:
                if int(round_baseline_model) == self.current_round:
                    aggregated_weights = load_fl_model_weights(path_file_created)
                    # update the weights of the new baseline model for this round
                    self.local_model.set_weights(aggregated_weights)
                    # fit the local model
                    history = self.local_model.fit(self.x_train, self.y_train, epochs=self.epochs)
                else:
                    logger.warning(
                        "The path %s does not correspond to the current round (%d), Skipping...",
                        path_file_created, self.current_round
                    )
            except ValueError:
                logger.warning(
                    "Malformed path %s, Skipping...",
                    path_file_created
                )
        else:
            # first round: the baseline model is in global_model_path
            history = self.local_model.fit(self.x_train, self.y_train, epochs=self.epochs)
        if history is not None:
            local_model_weights_path = os.path.join(
                self.local_model_weights_path,
                "weights_round_" + str(self.current_round) + ".json"
            )
            output_folder = Path(self.local_model_weights_path)
            output_folder.mkdir(parents=True, exist_ok=True)
            self.rounds2history[self.current_round] = history
            logger.info("Participant %s: end FL round %s", self.participant_id, self.current_round)
            self.current_round += 1
            save_fl_model_weights(self.local_model, local_model_weights_path)
        self.is_finished = self.current_round == self.n_fl_rounds
        return self.is_finished
