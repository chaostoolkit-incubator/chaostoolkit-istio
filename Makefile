.PHONY: install
install:
	pip install -r requirements.txt

.PHONY: install-dev
install-dev: install
	pip install -r requirements-dev.txt
	python setup.py develop

.PHONY: lint
lint:
	flake8 --ignore=E251 chaosistio/
	isort --check-only --profile black chaosistio/ tests/
	black --check --line-length=80 --diff chaosistio/ tests/

.PHONY: format
format:
	isort --profile black chaosistio/ tests/
	black --line-length=80 chaosistio/ tests/

.PHONY: tests
tests:
	pytest
