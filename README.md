[![ci](https://github.com/amenezes/rabbit-client/workflows/ci/badge.svg)](https://github.com/amenezes/rabbit-client/actions)
[![Maintainability](https://api.codeclimate.com/v1/badges/f24caeb9d85f17de93e2/maintainability)](https://codeclimate.com/github/amenezes/rabbit-client/maintainability)
[![codecov](https://codecov.io/gh/amenezes/rabbit-client/branch/master/graph/badge.svg)](https://codecov.io/gh/amenezes/rabbit-client)
[![PyPI version](https://badge.fury.io/py/rabbit-client.svg)](https://badge.fury.io/py/rabbit-client)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rabbit-client)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# rabbit-client

asyncio rabbit client powered by [aioamqp](https://github.com/Polyconseil/aioamqp).

rabbit-client provides a simple and automatic configuration to work with:  

  - pub/sub and [Dead Letter Exchanges](https://www.rabbitmq.com/dlx.html) with [rabbitmq](https://www.rabbitmq.com);  
  - [polling publisher pattern](https://microservices.io/patterns/data/polling-publisher.html) `out-of-box`;
  - connection and reconnection management with broker;
  - automatic channel configuration;
  - concurrent task execution `[optional]`;
  - automatic qos configuration;
  - different strategies to delay error events.

## Installing

Install and update using pip:

```bash
pip install -U rabbit-client
```

## Links

- License: [Apache License](https://choosealicense.com/licenses/apache-2.0/)
- Code: [https://github.com/amenezes/rabbit-client](https://github.com/amenezes/rabbit-client)
- Issue Tracker: [https://github.com/amenezes/rabbit-client/issues](https://github.com/amenezes/rabbit-client/issues)
- Documentation: [https://rabbit-client.amenezes.net](https://rabbit-client.amenezes.net)
