# Script used for linting on both python and solidity

pip install -r requirements/requirements-test.txt
npm install

pylint --fail-under=9 --ignore-patterns=test* --disable=W1514,E1101 decentralized_smart_grid_ml/ && \
solhint 'contracts/**/*.sol' -c ./.solhint.json