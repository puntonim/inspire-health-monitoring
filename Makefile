DEPS:=requirements/requirements-base.txt
VIRTUALENV=$(shell which virtualenv)
PIP:="venv/bin/pip"
CMD_FROM_VENV:=". venv/bin/activate; which"
PYTHON=$(shell "$(CMD_FROM_VENV)" "python2.7")

.PHONY: venv run requirements

default: run/prod;

venv:
	$(VIRTUALENV) -p $(shell which python2.7) venv
	. venv/bin/activate
	$(PIP) install -U "pip>=18.0" -q
	$(PIP) install -r $(DEPS)

run/qa:
	$(PYTHON) websearch_monitor.py qa

run/prod:
	$(PYTHON) websearch_monitor.py prod


## Utilities for the venv currently active.

requirements:
	pip install -U -r requirements.txt


## Generic utilities.

pyclean:
	find . -name *.pyc -delete

clean: pyclean
	rm -rf venv

cleanpipcache:
	rm -rf ~/Library/Caches/pip
