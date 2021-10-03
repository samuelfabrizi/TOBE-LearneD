"""
This module contains the function used to aggregate the local models' weights
in the global one
"""
from decentralized_smart_grid_ml.exceptions import NotValidClientsModelsError, NotValidAlphaVectorError
from decentralized_smart_grid_ml.utils.logging import create_logger

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
                aggregated_weights[idx_layer] = \
                    aggregated_weights[idx_layer] + \
                    local_layer_weights * alpha[idx_client]
            logger.debug("Update layer %d related to client %d", idx_layer, idx_client)
    logger.info("Finish models' weights aggregation of %d clients", len(alpha))
    return aggregated_weights
