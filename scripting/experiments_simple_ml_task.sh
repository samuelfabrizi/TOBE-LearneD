export PYTHONPATH="../"
export BC_ADDRESS="http://127.0.0.1:7545"
export ANNOUNCEMENT_JSON_PATH="/home/fabsam/Documenti/university/masterDegree/thesis/Decentralized-SmartGrid-ML/build/contracts/Announcement.json"
export DEX_JSON_PATH="/home/fabsam/Documenti/university/masterDegree/thesis/Decentralized-SmartGrid-ML/build/contracts/GreenDEX.json"
export TOKEN_JSON_PATH="/home/fabsam/Documenti/university/masterDegree/thesis/Decentralized-SmartGrid-ML/build/contracts/GreenToken.json"


# create the announcement
python create_announcement.py \
--contract_info_path \
/home/fabsam/Documenti/university/masterDegree/thesis/Decentralized-SmartGrid-ML/announcement_info.json \
--task_config_path \
/home/fabsam/Documenti/university/masterDegree/thesis/Decentralized-SmartGrid-ML/data_sample/simple_ml_task/simple_ml_task_config.json \
--test_set_path \
/home/fabsam/Documenti/university/masterDegree/thesis/Decentralized-SmartGrid-ML/data_sample/simple_ml_task/validator/simple_ml_task_test.csv \
--n_tokens_at_stake \
100000 \
--max_number_participants \
2 \
--percentage_reward_validator \
20 &

sleep 8


# run the validator
python validator_aggregation.py \
--contract_info_path \
/home/fabsam/Documenti/university/masterDegree/thesis/Decentralized-SmartGrid-ML/announcement_info.json \
--validation_set_path \
/home/fabsam/Documenti/university/masterDegree/thesis/Decentralized-SmartGrid-ML/data_sample/simple_ml_task/validator/simple_ml_task_validation.csv \
--test_set_path \
/home/fabsam/Documenti/university/masterDegree/thesis/Decentralized-SmartGrid-ML/data_sample/simple_ml_task/validator/simple_ml_task_test.csv \
--participant_weights_path \
/home/fabsam/Documenti/university/masterDegree/thesis/Decentralized-SmartGrid-ML/data_sample/simple_ml_task/participants \
--model_weights_new_round_path \
/home/fabsam/Documenti/university/masterDegree/thesis/Decentralized-SmartGrid-ML/data_sample/simple_ml_task/validator/ &

sleep 5

# run the participants
for idx_participant in 0 1
do
  python participant_fl_training.py \
  --contract_info_path \
  /home/fabsam/Documenti/university/masterDegree/thesis/Decentralized-SmartGrid-ML/announcement_info.json \
  --participant_id \
  $idx_participant \
  --validator_directory_path \
  /home/fabsam/Documenti/university/masterDegree/thesis/Decentralized-SmartGrid-ML/data_sample/simple_ml_task/validator &
  sleep 3
done