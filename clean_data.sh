#### delete simple ml task results ####

# delete the weights
find ./data_sample/simple_ml_task -type f -name '*weights*' -delete
# delete the datasets
find ./data_sample/simple_ml_task/validator -type f -name '*.csv' -delete
find ./data_sample/simple_ml_task/participants -type f -name '*.csv' -delete
# delete the participants statistics
find ./data_sample/simple_ml_task/participants -type f -name '*statistics*' -delete
# delete the validator statistics
find ./data_sample/simple_ml_task/validator -type f -name '*statistics*' -delete
# delete the models
rm -rf data_sample/simple_ml_task/linear_model
rm -rf data_sample/simple_ml_task/linear_model_config.json


#### delete appliance classification task results ####

# delete the weights
find ./data_sample/appliance_classification_task -type f -name '*weights*' -delete
# delete the participants directories
# find ./data_sample/appliance_classification_task/participants -type f -name '*.csv' -delete
# delete the datasets
#find ./data_sample/appliance_classification_task/validator -type f -name '*.csv' -delete
# delete the models
rm -rf data_sample/appliance_classification_task/model
rm -rf data_sample/appliance_classification_task/model_config.json


# delete the announcement info
rm -f announcement_info.json
# clean  the files created by python-coverage
coverage erase
# delete the files created by solidity-coverage
rm -rf coverage
rm -f coverage.json