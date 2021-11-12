# Script used for coverage test on python modules

pip install -r requirements/requirements-test.txt

coverage run -a --rcfile=./.coveragerc -m unittest
coverage report --fail-under=90

truffle run coverage
sh clean_data.sh