from decentralized_smart_grid_ml.federated_learning.federated_aggregator import weighted_average_aggregation
import pandas as pd
from tensorflow.keras.experimental import LinearModel
import numpy as np
import tensorflow as tf
from tensorflow import keras

train_set_path1 = "../data_sample/simple_ml_task/participants/participant_0/simple_ml_task_0.csv"
train_set_df1 = pd.read_csv(train_set_path1)
x_train1, y_train1 = train_set_df1[["x1", "x2"]].values[:10], train_set_df1["y"].values[:10]

train_set_path2 = "../data_sample/simple_ml_task/participants/participant_1/simple_ml_task_1.csv"
train_set_df2 = pd.read_csv(train_set_path2)
x_train2, y_train2 = train_set_df2[["x1", "x2"]].values, train_set_df2["y"].values

test_set_path = "../data_sample/simple_ml_task/validator/simple_ml_task_test.csv"
test_set_df = pd.read_csv(test_set_path)
x_test, y_test = test_set_df[["x1", "x2"]].values, test_set_df["y"].values

model1 = LinearModel(activation="sigmoid")
model1.compile(optimizer="sgd", loss="mse", metrics="accuracy")

model2 = LinearModel(activation="sigmoid")
model2.compile(optimizer="sgd", loss="mse", metrics="accuracy")

model1.fit(x_train1, y_train1, epochs=3)
model2.fit(x_train2, y_train2, epochs=3)

models = [model1, model2]

global_model = LinearModel(activation="sigmoid")
global_model.compile(optimizer="sgd", loss="mse", metrics="accuracy")
# here the fit function is called because it needs the build. The trained model will NOT be used becuase
# we will override its weights with the new ones
global_model.fit(x_train1, y_train1, epochs=1)

participants_weights = []
for model in models:
    participants_weights.append(model.get_weights())


from tensorflow.keras.layers import Layer, InputSpec
from tensorflow.keras import backend as K
from tensorflow.keras import initializers


class StackingWeightedEnsamble(keras.Sequential):

    def __init__(self, weak_models_weights, meta_model):
        super(StackingWeightedEnsamble, self).__init__()
        self.meta_model = meta_model
        self.weak_models_weights = weak_models_weights
        self.W = []
        for i in range(len(weak_models_weights)):
            weight = tf.Variable(
                0.5,
                trainable=True
            )
            self.W.append(weight)

    def compile(self, optimizer, loss, metrics):
        super(StackingWeightedEnsamble, self).compile(optimizer=optimizer, loss=loss, metrics=metrics)
        self.meta_model.compile(optimizer=optimizer, loss=loss, metrics=metrics)

    def call(self, x):
        new_weights = tf.math.scalar_mul(self.W[0], self.weak_models_weights[0])
        for weight, model_weight in zip(self.W[1:], self.weak_models_weights[1:]):
            new_weights += weight * model_weight
        self.meta_model.set_weights(new_weights)
        return self.meta_model(x)


if __name__ == '__main__':
    stacking_weighted = StackingWeightedEnsamble(participants_weights, global_model)
    stacking_weighted.compile(optimizer="sgd", loss="mse", metrics="accuracy")
    stacking_weighted.fit(x_test, y_test, epochs=10)


