# Script used for coverage test on python modules

pip install -r requirements/requirements.txt
pip install -r requirements/requirements.txt

coverage run -a --rcfile=./.coveragerc -m unittest
coverage report --fail-under=90
