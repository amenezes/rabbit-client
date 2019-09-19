.DEFAULT_GOAL := about
RABBIT_INSTANCE := $(shell docker-compose -f example/docker-compose.yml ps | grep rabbit | wc -l)

flake:
	@echo "> code style checking"
	flake8 rabbit
	flake8 tests

clean:
	@echo "> cleaning development environment"
	docker-compose -f example/docker-compose.yml down -v
	docker system prune -f

tests:
	@echo "> unittest"
ifeq ($(RABBIT_INSTANCE), 0)
	docker-compose -f example/docker-compose.yml up -d rabbit
	sleep 10
endif
	@echo "> applying database migrations"
	python -m pytest -v --cov-report xml --cov-report term --cov=rabbit tests

doc: 
	@echo "> generate project documentation..."

install-deps:
	@echo "> installing dependencies..."
	pip install -r requirements-dev.txt

venv:
	@echo "> preparing local development environment"
	pip install virtualenv
	virtualenv venv

about:
	@echo "> rabbit-client"
	@echo ""
	@echo "make flake        - Flake8 lint."
	@echo "make tests        - Execute tests."
	@echo "make doc          - Generate project documentation."
	@echo "make install-deps - Install development dependencies."
	@echo "make venv         - Install virtualenv and create venv directory."
	@echo ""
	@echo "mailto: alexandre.fmenezes@gmail.com"

ci:
	@echo "> "

all: flake tests doc docker-pub clean


.PHONY: flake clean tests doc install-deps venv ci all
