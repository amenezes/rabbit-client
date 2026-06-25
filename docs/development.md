# Development

First clone the [rabbit-client](https://github.com/amenezes/rabbit-client) repository and create a virtual environment.

## Setup environment

### Provisioning RabbitMQ

To run RabbitMQ locally use the docker-compose file present in the root directory:

```bash
docker-compose up -d
```

This starts a RabbitMQ broker with the management plugin. The broker listens on:

| Service | URL |
|---------|-----|
| AMQP | `amqp://guest:guest@localhost:5672/` |
| Management UI | [http://localhost:15672](http://localhost:15672) (guest/guest) |

To stop the broker:

```bash
docker-compose down
```

!!! warning "Integration tests"
    The test suite includes integration tests (under `tests/integration/`) that require a running RabbitMQ broker. Without Docker, these tests are automatically skipped.

### Install development dependencies

**Option 1** — Using make target (also installs pre-commit hooks):

```bash
make install-deps
```

**Option 2** — Using uv directly:

```bash
uv sync --dev --all-extras
uv run pre-commit install
```

## Pre-commit hooks

Pre-commit runs the following checks automatically on every `git commit`:

| Hook | Scope |
|------|-------|
| black | Python formatting |
| isort | Import sorting (`--profile black`) |
| flake8 | Linting |
| mypy | Static type checking |
| forbid-crlf | Line endings |
| check-case-conflict | Filename case conflicts |
| check-merge-conflict | Merge conflict markers |
| end-of-file-fixer | Trailing newline |
| check-yaml | YAML validation |
| check-added-large-files | File size guard |

To run all hooks manually without committing:

```bash
uv run pre-commit run --all-files
```

## Lint

Runs the full pipeline: isort → black → flake8 → mypy.

```bash
make lint
```

To skip formatting (isort + black) — useful when iterating on type errors:

```bash
SKIP_STYLE=1 make lint
```

To run individual tools:

```bash
uv run mypy rabbit               # type checking only
uv run flake8 rabbit tests       # linting only
uv run black --check rabbit      # format check only
```

## Tests

### Unit tests

Unit tests use mocked AMQP channels and require no broker. They run fast and are always executed:

```bash
make tests
```

Under the hood this runs:

```bash
uv run pytest -vv --no-cov-on-fail --cov=rabbit tests
```

### Running specific tests

```bash
# Single test file
uv run pytest tests/unit/test_dlx.py -v

# Specific test function
uv run pytest tests/unit/test_subscribe.py::test_configure_sets_prefetch_to_concurrent -v

# By keyword
uv run pytest tests/ -k "dlx" -v
```

### Integration tests

Integration tests (under `tests/integration/`) require a running RabbitMQ broker (`docker-compose up -d`). They are marked with `@pytest.mark.integration` and are automatically skipped if the broker is unreachable.

```bash
# Run integration tests only
uv run pytest tests/integration/ -v

# Run everything (unit + integration)
uv run pytest tests/ -v
```

### Coverage

Coverage reports are generated in the project root:

| Format | File |
|--------|------|
| Terminal summary | Printed by `make tests` |
| XML | `coverage.xml` |
| HTML | `htmlcov/index.html` (`uv run coverage html` first) |

Lines containing `logging.info` / `logging.debug` / `logging.warn` are excluded from the report.

## Documentation

To preview documentation changes locally:

```bash
make docs
```

This copies `README.md` → `docs/index.md` and serves the site via mkdocs at [http://localhost:8000](http://localhost:8000) with live reload.

The documentation uses [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/). Configuration is in `mkdocs.yml`.

## CI

The equivalent of what GitHub Actions runs can be executed locally:

```bash
make ci
```

This runs `lint` + `tests` (same as the CI pipeline). Always run this before opening a pull request.

## Code conventions

### attrs patterns

- `@mutable` — for objects with mutable state (`AioRabbitClient`, `Subscribe`, `Publish`, `DLX`)
- `@frozen` — for immutable value objects (`Exchange`, `Queue`)
- `init=False` — for fields injected after construction (channels, live exchange/queue proxies)
- Private fields prefixed with `_`: `_channel`, `_main_exchange`, `_main_queue`

### Message handling

`Subscribe._handle_message` uses `message.process(ignore_processed=True)` to take full control of ack/nack. On success the message is acked. On failure the message is acked AND a copy is published to the DLX exchange with a per-message `expiration`.

### Delay strategies

`_wait.py` exports three pure functions (`constant`, `expo`, `fibo`) that take `headers` and optional parameters, returning a delay in milliseconds. They read `x-delay` from message headers to support accumulated backoff across retries.

### Version

The version is stored in `rabbit/__init__.py` as `__version__` and parsed by the Makefile.

!!! note "Python versions"
    The CI matrix tests against Python 3.11, 3.12, 3.13, and 3.14. Python >= 3.11 is required.
