find ./data_sample/simple_ml_task -type f -name '*weights*' -delete
find ./data_sample/simple_ml_task/participants -type f -name '*.csv' -delete
find ./data_sample/simple_ml_task/validator -type f -name '*.csv' -delete
rm -rf data_sample/simple_ml_task/linear_model
rm -rf data_sample/simple_ml_task/linear_model_config.json
rm announcement_info.json
