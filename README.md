[![Build Status](https://travis-ci.org/amenezes/rabbit-client.svg?branch=master)](https://travis-ci.org/amenezes/rabbit-client)
[![Maintainability](https://api.codeclimate.com/v1/badges/f24caeb9d85f17de93e2/maintainability)](https://codeclimate.com/github/amenezes/rabbit-client/maintainability)
[![codecov](https://codecov.io/gh/amenezes/rabbit-client/branch/master/graph/badge.svg)](https://codecov.io/gh/amenezes/rabbit-client)
[![PyPI version](https://badge.fury.io/py/rabbit-client.svg)](https://badge.fury.io/py/rabbit-client)

# rabbit-client

asyncio rabbit client powered by [aioamqp](https://github.com/Polyconseil/aioamqp).

rabbit-client provides a simple and automatic configuration to work with pub/sub and [Dead Letter Exchanges](https://www.rabbitmq.com/dlx.html) with [rabbitmq](https://www.rabbitmq.com).

The image below exemplifies the workflow implemented by the client.

![rabbit-client-workflow](./docs/rabbit-client-workflow.png)

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

## Usage example

To run the example locally clone the project repo, install your dependencies and run:

`consumer`:

```bash
python test_client.py
```

`producer`:

```bash
python test_producer.py
```

### Consumer code

```python
import asyncio
import logging

from aiohttp import web

from rabbit.client import AioRabbitClient
from rabbit.publish import Publish
from rabbit.subscribe import Subscribe


async def handle_info(request):
    return web.json_response({'app': 'aio-rabbit-client'})


async def handle_status(request):
    return web.json_response({'status': 'UP'})


def configure_default_client(app):
    client = AioRabbitClient(app=app.loop)
    consumer = Subscribe(client, publish=Publish())
    app.loop.create_task(consumer.configure())
    app['rabbit_client'] = client


logging.getLogger().setLevel(logging.DEBUG)
loop = asyncio.get_event_loop()
app = web.Application(loop=loop)
app.add_routes([
    web.get('/manage/health', handle_status),
    web.get('/manage/info', handle_info)
])
configure_default_client(app)
web.run_app(app, host='0.0.0.0', port=5000)
```

### Producer code

```python
import asyncio
import json
import os

from rabbit.client import AioRabbitClient
from rabbit.exchange import Exchange
from rabbit.publish import Publish
from rabbit.queue import Queue


loop = asyncio.get_event_loop()

publish = Publish(
    AioRabbitClient(loop),
    exchange=Exchange(
        name=os.getenv('SUBSCRIBE_EXCHANGE', 'default.in.exchange'),
        exchange_type=os.getenv('SUBSCRIBE_EXCHANGE_TYPE', 'topic'),
        topic=os.getenv('SUBSCRIBE_TOPIC', '#')
    ),
    queue=Queue(
        name=os.getenv('SUBSCRIBE_QUEUE', 'default.subscribe.queue')
    )
)
loop.run_until_complete(publish.configure())
print(
    "[>] Event sent to: "
    f"[exchange: {os.getenv('SUBSCRIBE_EXCHANGE', 'default.in.exchange')}"
    f" | topic: {os.getenv('SUBSCRIBE_TOPIC', '#')} | "
    f"subscribe: {os.getenv('SUBSCRIBE_QUEUE', 'default.subscribe.queue')}]"
)

payload = {
    'document': 1,
    'description': '123',
    'documentSearchable': None,
    'pages': [
        {
            'body': 'abc 123',
            'number': 1
        },
        {
            'body': 'def 456',
            'number': 2
        },
        {
            'body': 'ghi 789',
            'number': 3
        }
    ]
}

loop.run_until_complete(
    publish.send_event(
        bytes(json.dumps(payload), 'utf-8')
        # properties={'headers': {'x-delay': 5000}}
    )
)
```

## Development

Install development dependencies.

```bash
make install-deps
```

To execute lint:

```bash
make lint
```

To execute tests just run:
```bash
make tests
```

## Links

- License: [Apache License](https://choosealicense.com/licenses/apache-2.0/)
- Code: https://github.com/amenezes/rabbit-client
- Issue Tracker: https://github.com/amenezes/rabbit-client/issues