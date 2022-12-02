.DEFAULT_GOAL := about
VERSION := $(shell cat rabbit/__init__.py | grep '__version__ ' | cut -d'"' -f 2)

lint:
ifeq ($(SKIP_STYLE), )
	@echo "> running isort..."
	isort --profile black rabbit
	isort --profile black tests
	isort --profile black setup.py
	@echo "> running black..."
	black rabbit
	black tests
	black setup.py
endif
	@echo "> running flake8..."
	flake8 rabbit
	flake8 tests
	flake8 setup.py
	@echo "> running mypy..."
	mypy rabbit

tests:
	@echo "> unittest"
	python -m pytest -vv --no-cov-on-fail --color=yes --cov-report xml --cov-report term --cov=rabbit tests

docs:
	@echo "> generate project documentation..."
	@cp README.md docs/index.md
	mkdocs serve

install-deps:
	@echo "> installing dependencies..."
	pip install -r requirements-dev.txt

tox:
	@echo "> running tox..."
	tox -r -p all

about:
	@echo "> rabbit-client: $(VERSION)"
	@echo ""
	@echo "make lint         - Runs: [isort > black > flake8 > mypy]"
	@echo "make tox          - Runs tox."
	@echo "make tests        - Execute tests."
	@echo "make docs         - Generate project documentation."
	@echo "make install-deps - Install development dependencies."
	@echo ""
	@echo "mailto: alexandre.fmenezes@gmail.com"

ci: lint tests
ifeq ($(TRAVIS_PULL_REQUEST), false)
	@echo "> download CI dependencies"
	curl -L https://codeclimate.com/downloads/test-reporter/test-reporter-latest-linux-amd64 > ./cc-test-reporter
	chmod +x ./cc-test-reporter
	@echo "> uploading report..."
	codecov --file coverage.xml -t $$CODECOV_TOKEN
	./cc-test-reporter format-coverage -t coverage.py -o codeclimate.json
	./cc-test-reporter upload-coverage -i codeclimate.json -r $$CC_TEST_REPORTER_ID
endif

all: install-deps ci tox docs

.PHONY: install-deps lint tests docs tox ci all
