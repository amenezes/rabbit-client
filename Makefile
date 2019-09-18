.DEFAULT_GOAL := about
RABBIT_INSTANCE := $(shell docker-compose ps | grep rabbit | wc -l)

flake:
	@echo "--- code style checking ---"
	flake8 app
	flake8 tests

clean:
	@echo "--- cleaning development environment ---"
	docker-compose down -v
	docker system prune -f

tests:
	@echo "--- unittest ---"
ifeq ($(RABBIT_INSTANCE), 0)
	docker-compose up -d rabbit
	sleep 10
endif
ifeq ($(POSTGRES_INSTANCE), 0)
	docker-compose up -d postgres
	sleep 10
endif
	@echo "--- applying database migrations ---"
	alembic -c app/alembic.ini -n local_db upgrade head
	sleep 10
	python -m pytest -v --cov-report xml --cov-report term --cov=app tests

doc: 
	@echo "> generate project documentation..."

install-deps:
	@echo "> installing dependencies..."
	pip install -r requirements-dev.txt
ifeq ($(STFDIGITAL_SHARED), 1)
	git clone git@gitlab.com:supremotribunalfederal/stfdigital/integracoes/shared.git
endif

venv:
	@echo "> preparing local development environment"
	pip install virtualenv
	virtualenv venv



ci:
	@echo ""

all: flake tests doc docker-pub clean


.PHONY: flake clean tests doc install-deps venv ci all
