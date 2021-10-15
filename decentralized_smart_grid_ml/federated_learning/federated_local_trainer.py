"""
This module contains the class responsible for the training of the local participant's model
"""
import pandas as pd

from decentralized_smart_grid_ml.federated_learning.models_reader_writer import load_fl_model


class FederatedLocalTrainer:
    """ This class is responsible for the training of the local participant's model """

    def __init__(self, participant_id, n_fl_rounds, global_model_path,
                 train_set_path, epochs, local_model_weights_path):
        self.participant_id = participant_id
        self.n_fl_rounds = n_fl_rounds
        self.global_model_path = load_fl_model(global_model_path)
        train_set_df = pd.read_csv(train_set_path)
        # TODO: generalize this function to extract features and labels from the dataset
        self.x_train, self.y_train = train_set_df[["x1", "x2"]].values, train_set_df["y"].values
        self.epochs = epochs
        self.local_model_weights_path = local_model_weights_path
        self.rounds2history = {}
        self._initialize_rounds2history()
        self.current_round = 0

    def _initialize_rounds2history(self):
        """
        Initialize the rounds to history information mapping
        :return:
        """
        for idx_round in range(self.n_fl_rounds):
            self.rounds2history[idx_round] = None

