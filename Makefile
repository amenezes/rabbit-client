.DEFAULT_GOAL := about
RABBIT_INSTANCE := $(shell docker-compose -f example/docker-compose.yml ps | grep rabbit | wc -l)
VENV_DIR := $(shell [ ! -d "venv" ] && echo 1 || echo 0)
CLEAN_TEST_ENV := "true"

lint:
	@echo "> executing flake8 to check codestyle..."
	flake8 rabbit
	flake8 tests
	@echo "> executing mypy static type checker..."
	mypy rabbit

clean:
	@echo "> cleaning development environment"
	docker-compose -f example/docker-compose.yml down -v
	docker system prune -f

tests:
	@echo "> unittest"
ifeq ($(RABBIT_INSTANCE), 0)
	@echo "> initializing rabbit container..."
	docker-compose -f example/docker-compose.yml up -d rabbit
	sleep 15
endif
	python -m pytest -v --cov-report xml --cov-report term --cov=rabbit tests
ifeq ($(CLEAN_TEST_ENV), "true")
	@echo "> cleaning test environment..."
	make clean
endif

doc: 
	@echo "> generate project documentation..."

install-deps:
	@echo "> installing dependencies..."
	pip install -r requirements-dev.txt

venv:
ifeq ($(VENV_DIR), 1)
	@echo "> preparing local development environment"
	pip install virtualenv
	virtualenv venv
else
	@echo "> venv already exists!"
endif

about:
	@echo "> rabbit-client"
	@echo ""
	@echo "make lint         - Runs flake8 and mypy."
	@echo "make tests        - Execute tests."
	@echo "make doc          - Generate project documentation."
	@echo "make install-deps - Install development dependencies."
	@echo "make venv         - Install virtualenv and create venv directory."
	@echo ""
	@echo "mailto: alexandre.fmenezes@gmail.com"

ci:
	@echo "> download CI dependencies"
	curl -L https://codeclimate.com/downloads/test-reporter/test-reporter-latest-linux-amd64 > ./cc-test-reporter
	chmod +x ./cc-test-reporter
	@echo "> uploading report..."
	codecov --file coverage.xml -t $$CODECOV_TOKEN
	./cc-test-reporter format-coverage -t coverage.py -o codeclimate.json
	./cc-test-reporter upload-coverage -i codeclimate.json -r $$CC_TEST_REPORTER_ID

all: flake tests doc docker-pub clean


.PHONY: flake clean tests doc install-deps venv ci all
