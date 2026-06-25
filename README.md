[![ci](https://github.com/amenezes/rabbit-client/workflows/ci/badge.svg)](https://github.com/amenezes/rabbit-client/actions)
[![codecov](https://codecov.io/gh/amenezes/rabbit-client/branch/master/graph/badge.svg)](https://codecov.io/gh/amenezes/rabbit-client)
[![PyPI version](https://badge.fury.io/py/rabbit-client.svg)](https://badge.fury.io/py/rabbit-client)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rabbit-client)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# rabbit-client

asyncio rabbit client powered by [aio-pika](https://github.com/mosquito/aio-pika).

rabbit-client provides a simple and automatic configuration to work with:  

  - pub/sub and [Dead Letter Exchanges](https://www.rabbitmq.com/dlx.html) with [rabbitmq](https://www.rabbitmq.com);  
  - [polling publisher pattern](https://microservices.io/patterns/data/polling-publisher.html) `out-of-box`;
  - connection and reconnection management with broker (powered by `connect_robust`);
  - automatic channel configuration;
  - concurrent task execution `[optional]`;
  - automatic qos configuration;
  - different strategies to delay error events.

## Installing

Install and update using [uv](https://docs.astral.sh/uv/):

```bash
# Add as a project dependency (recommended)
uv add rabbit-client

# Or install globally / in any virtual environment
uv pip install -U rabbit-client
```

## Links

- License: [Apache License](https://choosealicense.com/licenses/apache-2.0/)
- Code: [https://github.com/amenezes/rabbit-client](https://github.com/amenezes/rabbit-client)
- Issue Tracker: [https://github.com/amenezes/rabbit-client/issues](https://github.com/amenezes/rabbit-client/issues)
- Documentation: [https://rabbit-client.amenezes.net](https://rabbit-client.amenezes.net)
