# This Makefile requires the following commands to be available:
# * virtualenv
# * python2

DEPS:=requirements/requirements-base.txt
VIRTUALENV=$(shell which virtualenv)
PIP:="venv/bin/pip"
CMD_FROM_VENV:=". venv/bin/activate; which"
PYTHON=$(shell "$(CMD_FROM_VENV)" "python2.7")

.PHONY: venv qa prod requirements pyclean clean pipclean

default: qa;

venv:
	$(VIRTUALENV) -p $(shell which python2.7) venv
	. venv/bin/activate
	$(PIP) install -U "pip>=18.0" -q
	$(PIP) install -r $(DEPS)

_make_venv_if_empty:
	@[ -e ./venv/bin/python ] || make venv

qa: _make_venv_if_empty
	$(PYTHON) health_monitor.py qa

prod: _make_venv_if_empty
	$(PYTHON) health_monitor.py prod


## Utilities for the venv currently active.

_ensure_active_env:
ifndef VIRTUAL_ENV
	@echo 'Error: no virtual environment active'
	@exit 1
endif

requirements: _ensure_active_env
	pip install -U -r $(DEPS)


## Generic utilities.

pyclean:
	find . -name *.pyc -delete
	rm -rf *.egg-info build
	rm -rf coverage.xml .coverage
	rm -rf .pytest_cache

clean: pyclean
	rm -rf venv
	rm -rf .tox
	rm -rf dist

pipclean:
	rm -rf ~/Library/Caches/pip
	rm -rf ~/.cache/pip