#### delete simple ml task results ####


# delete the participants' directory
rm -rf ./data_sample/simple_ml_task/participants
# delete the validator's directory
rm -rf ./data_sample/simple_ml_task/validator
# delete models info
rm -rf data_sample/simple_ml_task/model
rm -rf data_sample/simple_ml_task/model_config.json
rm -rf data_sample/simple_ml_task/model_weights

#### delete simple multi-classification task results ####

# delete the participants' directory
rm -rf ./data_sample/simple_multiclass_task/participants
# delete the validator's directory
rm -rf ./data_sample/simple_multiclass_task/validator
# delete models info
rm -rf data_sample/simple_multiclass_task/model
rm -rf data_sample/simple_multiclass_task/model_config.json
rm -rf data_sample/simple_multiclass_task/model_weights


#### delete appliance classification task results ####

# delete the participants' directory
rm -rf ./data_sample/appliance_classification_task/participants
# delete the validator's directory
rm -rf ./data_sample/appliance_classification_task/validator
# delete models info
rm -rf data_sample/appliance_classification_task/model
rm -rf data_sample/appliance_classification_task/model_config.json
rm -rf data_sample/appliance_classification_task/model_weights


# delete the announcement info
rm -f announcement_info.json
# clean  the files created by python-coverage
coverage erase
# delete the files created by solidity-coverage
rm -rf coverage
rm -f coverage.json