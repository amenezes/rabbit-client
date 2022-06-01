# Development

First clone the [rabbit-client](https://github.com/amenezes/rabbit-client) repository and create a virtual environment.

## Setup environment

### provisioning the environment

To run RabbitMQ locally can you use docker-compose file present in the root directory. So just run:

```bash
docker-compose up -d
```

### Install development dependencies

**option 1**

Using make target:

```bash
make install-deps
```

**option 2**

Using pip

```bash
pip install -r requirements-dev.txt
```

## Lint

Runs: isort > black > flake8 > mypy.

```bash
make lint
```

## Tests

Execute all unit tests.

```bash
make tests
```

## Tox

Run `Lint` and `Tests` on python: `3.8`, `3.9` and `3.10`

```bash
make tox
```
