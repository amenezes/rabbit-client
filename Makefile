.DEFAULT_GOAL := about
VERSION := $(shell cat rabbit/__init__.py | grep '__version__ ' | cut -d'"' -f 2)

lint:
ifeq ($(SKIP_STYLE), )
	@echo "> running isort..."
	isort rabbit
	isort tests
	@echo "> running black..."
	black rabbit
	black tests
endif
	@echo "> running flake8..."
	flake8 rabbit
	flake8 tests
	@echo "> running mypy..."
	mypy rabbit

tests:
	@echo "> unittest"
	python -m pytest -vv --no-cov-on-fail --color=yes --cov-report xml --cov-report term --cov=rabbit tests

docs:
	@echo "> generate project documentation..."
	@cp README.md docs/index.md
	mkdocs serve -a 0.0.0.0:8000

install-deps:
	@echo "> installing dependencies..."
	uv pip install -r requirements-dev.txt
	pre-commit install

about:
	@echo "> rabbit-client: $(VERSION)"
	@echo ""
	@echo "make lint         - Runs: [isort > black > flake8 > mypy]"
	@echo "make tests        - Execute tests."
	@echo "make docs         - Generate project documentation."
	@echo "make install-deps - Install development dependencies."
	@echo ""
	@echo "mailto: alexandre.fmenezes@gmail.com"

ci: lint tests
ifeq ($(GITHUB_HEAD_REF), false)
	codecov --file coverage.xml -t $$CODECOV_TOKEN
endif

all: install-deps ci docs

.PHONY: install-deps lint tests docs ci all
