#!/bin/bash

# constants
N_PARTICIPANTS=5

# environment variables
export PYTHONPATH="../"
export BC_ADDRESS="http://127.0.0.1:7545"
export ANNOUNCEMENT_JSON_PATH="/home/fabsam/Documenti/university/masterDegree/thesis/Decentralized-SmartGrid-ML/build/contracts/Announcement.json"
export DEX_JSON_PATH="/home/fabsam/Documenti/university/masterDegree/thesis/Decentralized-SmartGrid-ML/build/contracts/GreenDEX.json"
export TOKEN_JSON_PATH="/home/fabsam/Documenti/university/masterDegree/thesis/Decentralized-SmartGrid-ML/build/contracts/GreenToken.json"

cd ..
sh clean_data.sh
truffle migrate --reset
cd scripting/

python dataset_task_initialization.py \
--dataset_path \
/home/fabsam/Documenti/university/masterDegree/thesis/Decentralized-SmartGrid-ML/data_sample/simple_multiclass_task/simple_multiclass_task.csv \
--validation_size \
0.2 \
--test_size \
0.15 \
--n_participants \
$N_PARTICIPANTS \
--ml_task_directory_path \
/home/fabsam/Documenti/university/masterDegree/thesis/Decentralized-SmartGrid-ML/data_sample/simple_multiclass_task/ \
--random_state \
42 \
--shuffle \
--unbalanced

# create the announcement
python create_announcement.py \
--contract_info_path \
/home/fabsam/Documenti/university/masterDegree/thesis/Decentralized-SmartGrid-ML/announcement_info.json \
--task_config_path \
/home/fabsam/Documenti/university/masterDegree/thesis/Decentralized-SmartGrid-ML/data_sample/simple_multiclass_task/simple_multiclass_task_config.json \
--test_set_path \
/home/fabsam/Documenti/university/masterDegree/thesis/Decentralized-SmartGrid-ML/data_sample/simple_multiclass_task/validator/simple_multiclass_task_test.csv \
--n_tokens_at_stake \
10000000 \
--max_number_participants \
$N_PARTICIPANTS \
--percentage_reward_validator \
15 &

sleep 8


# run the validator
python validator_aggregation.py \
--contract_info_path \
/home/fabsam/Documenti/university/masterDegree/thesis/Decentralized-SmartGrid-ML/announcement_info.json \
--validation_set_path \
/home/fabsam/Documenti/university/masterDegree/thesis/Decentralized-SmartGrid-ML/data_sample/simple_multiclass_task/validator/simple_multiclass_task_validation.csv \
--test_set_path \
/home/fabsam/Documenti/university/masterDegree/thesis/Decentralized-SmartGrid-ML/data_sample/simple_multiclass_task/validator/simple_multiclass_task_test.csv \
--participant_weights_path \
/home/fabsam/Documenti/university/masterDegree/thesis/Decentralized-SmartGrid-ML/data_sample/simple_multiclass_task/participants \
--model_weights_new_round_path \
/home/fabsam/Documenti/university/masterDegree/thesis/Decentralized-SmartGrid-ML/data_sample/simple_multiclass_task/validator/ &

sleep 5

# run the participants
for (( idx_participant=0; idx_participant<$N_PARTICIPANTS; idx_participant++ ))
do
  python participant_fl_training.py \
  --contract_info_path \
  /home/fabsam/Documenti/university/masterDegree/thesis/Decentralized-SmartGrid-ML/announcement_info.json \
  --participant_id \
  $idx_participant \
  --validator_directory_path \
  /home/fabsam/Documenti/university/masterDegree/thesis/Decentralized-SmartGrid-ML/data_sample/simple_multiclass_task/validator &
  sleep 3
done