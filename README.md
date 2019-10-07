[![Build Status](https://travis-ci.org/amenezes/rabbit-client.svg?branch=master)](https://travis-ci.org/amenezes/rabbit-client)
[![Maintainability](https://api.codeclimate.com/v1/badges/f24caeb9d85f17de93e2/maintainability)](https://codeclimate.com/github/amenezes/rabbit-client/maintainability)
[![codecov](https://codecov.io/gh/amenezes/rabbit-client/branch/master/graph/badge.svg)](https://codecov.io/gh/amenezes/rabbit-client)
[![PyPI version](https://badge.fury.io/py/rabbit-client.svg)](https://badge.fury.io/py/rabbit-client)

# rabbit-client

asyncio rabbit client powered by [aioamqp](https://github.com/Polyconseil/aioamqp).

rabbit-client provides a simple and automatic configuration to work with:  
- pub/sub and [Dead Letter Exchanges](https://www.rabbitmq.com/dlx.html) with [rabbitmq](https://www.rabbitmq.com);  
- [polling publisher pattern](https://microservices.io/patterns/data/polling-publisher.html).

## Installing

Install and update using pip:

```bash
pip install -U rabbit-client
```

## Dependencies

- [attrs](http://www.attrs.org/en/stable/)
- [aioamqp](https://github.com/polyconseil/aioamqp)

## Setup

All values expected to configure rabbitmq can be set via environment variables.

### Default values

```.env
# publish/producer
PUBLISH_EXCHANGE=default.out.exchange
PUBLISH_EXCHANGE_TYPE=topic
PUBLISH_TOPIC=#
PUBLISH_QUEUE=default.publish.queue

# subscribe/consumer
SUBSCRIBE_EXCHANGE=default.in.exchange
SUBSCRIBE_EXCHANGE_TYPE=topic
SUBSCRIBE_TOPIC=#
SUBSCRIBE_QUEUE=default.subscribe.queue

# dlx
DLX_EXCHANGE=DLX
DLX_TYPE=direct
DQL_QUEUE=default.subscribe.queue.dlq
```

## Links

- License: [Apache License](https://choosealicense.com/licenses/apache-2.0/)
- Code: [https://github.com/amenezes/rabbit-client](https://github.com/amenezes/rabbit-client)
- Issue Tracker: [https://github.com/amenezes/rabbit-client/issues](https://github.com/amenezes/rabbit-client/issues)
- Documentation: [https://rabbit-client.amenezes.dev](https://rabbit-client.amenezes.dev)