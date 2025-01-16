.PHONY: install test lint build publish clean

# Variables
PACKAGE_NAME=android_sms_gateway
VERSION=$(shell grep '__version__' $(PACKAGE_NAME)/__init__.py | cut -d '"' -f 2)

# Install pipenv and project dependencies
install:
	pipenv install --dev --categories encryption

# Run tests with pytest or unittest
test:
	pipenv run python -m pytest tests

# Lint the project with flake8
lint:
	pipenv run flake8 $(PACKAGE_NAME) tests

# Build the project
build:
	pipenv run python -m build

# Publish the library to PyPI
publish:
	pipenv run twine upload dist/*

# Clean up the project directory
clean:
	pipenv --rm
	rm -rf dist build $(PACKAGE_NAME).egg-info
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete