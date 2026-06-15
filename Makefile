.DEFAULT_GOAL := about
VERSION := $(shell cat rabbit/__init__.py | grep '__version__ ' | cut -d'"' -f 2)

lint:
ifeq ($(SKIP_STYLE), )
	@echo "> running isort..."
	uv run isort rabbit
	uv run isort tests
	@echo "> running black..."
	uv run black rabbit
	uv run black tests
endif
	@echo "> running flake8..."
	uv run flake8 rabbit
	uv run flake8 tests
	@echo "> running mypy..."
	uv run mypy rabbit

tests:
	@echo "> unittest"
	uv run pytest -vv --no-cov-on-fail --color=yes --cov-report xml --cov-report term --cov=rabbit tests

docs:
	@echo "> generate project documentation..."
	@cp README.md docs/index.md
	uv run mkdocs serve -a 0.0.0.0:8000

install-deps:
	@echo "> installing dependencies..."
	uv sync --dev --all-extras
	uv run pre-commit install

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

all: install-deps ci docs

.PHONY: install-deps lint tests docs ci all
