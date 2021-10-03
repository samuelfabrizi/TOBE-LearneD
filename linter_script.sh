# Script used for linting on python code

pip install -r requirements/requirements.txt
pip install -r requirements/requirements.txt

pylint --fail-under=9 --ignore-patterns=test* --disable=W1514 decentralized_smart_grid_ml/federated_learning
