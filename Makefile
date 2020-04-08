.DEFAULT_GOAL := about
VERSION := $(shell cat rabbit/__version__.py | cut -d'"' -f 2)
SKIP_STYLE := $(shell printenv SKIP_STYLE | wc -l)

lint:
ifeq ($(SKIP_STYLE), 0)
	@echo "> running isort..."
	isort -rc rabbit/
	isort -rc tests/
	@echo "> running black..."
	black --exclude=rabbit/migrations rabbit
	black tests
endif
	@echo "> running flake8..."
	flake8 rabbit
	flake8 tests
	@echo "> running mypy..."
	mypy rabbit

tests:
	@echo "> unittest"
	python -m pytest -v --cov-report xml --cov-report term --cov=rabbit tests

docs:
	@echo "> generate project documentation..."
	portray server

install-deps:
	@echo "> installing dependencies..."
	pip install -r requirements-dev.txt

tox:
	@echo "> running tox..."
	tox -r -p all

about:
	@echo "> rabbit-client | v$(VERSION)"
	@echo ""
	@echo "make lint         - Runs: [isort > black > flake8 > mypy]"
	@echo "make tox          - Runs tox."
	@echo "make tests        - Execute tests."
	@echo "make docs         - Generate project documentation."
	@echo "make install-deps - Install development dependencies."
	@echo ""
	@echo "mailto: alexandre.fmenezes@gmail.com"

ci: lint tests
ifeq ($(CI), true)
	@echo "> download CI dependencies"
	curl -L https://codeclimate.com/downloads/test-reporter/test-reporter-latest-linux-amd64 > ./cc-test-reporter
	chmod +x ./cc-test-reporter
	@echo "> uploading report..."
	codecov --file coverage.xml -t $$CODECOV_TOKEN
	./cc-test-reporter format-coverage -t coverage.py -o codeclimate.json
	./cc-test-reporter upload-coverage -i codeclimate.json -r $$CC_TEST_REPORTER_ID
endif

all: install-deps ci docs

.PHONY: install-deps lint tests docs tox ci all
