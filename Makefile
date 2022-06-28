SHELL := /bin/bash
.ONESHELL:
.PHONY: clean clean-test clean-pyc clean-build
.DEFAULT_GOAL := show-commands

show-commands:
	@echo "make install: install package and dependecies"
	@echo "make test   : run unit tests"
	@echo "make clean  : remove Python build, test artifacts"
	@echo "make run    : run local server"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr ldist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

install: install-dev
	@echo "Installing package"
	pip install .

install-dev:
	@echo "Installing development requirements"
	pip install --upgrade pip
	pip install -e ".[dev]"

test:
	pytest

run:
	@flask run