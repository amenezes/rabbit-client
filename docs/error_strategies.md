## Delay strategies

- [Scheduling Messages with RabbitMQ](https://blog.rabbitmq.com/posts/2015/04/scheduling-messages-with-rabbitmq)

### expo

Exponential backoff time, inspired in the great library [backoff](https://github.com/litl/backoff).

By default a cycle with 3 iteractions will produces:

```txt linenums="1"
600000 # 10 minutes
1200000 # 20 minutes
2400000 # 40 minutes
```

#### configuration

```ini linenums="1"
# delay
EXPO_DELAY=300000

# base
EXPO_BASE=2

# factor
EXPO_FACTOR=1

# max_delay
EXPO_MAX_DELAY= # there's no limit by default
```

### fibo

Incremental delay by minute.

By default a cycle with 3 iteractions will produces:

```txt linenums="1"
1. 360000 # 6 minutes
2. 420000 # 7 minutes
3. 480000 # 8 minutes
```

#### configuration

```ini
# delay
FIBO_DELAY=300000

# max_delay
FIBO_MAX_DELAY=86400000 # 1 day
```

### constant

Constant time.

By default a cycle with 3 iteractions will produces:

```txt linenums="1"
300000 # 5 minutes 
300000 # 5 minutes
300000 # 5 minutes
```

> **constant** strategy it's the default option for Subscribe.

#### configuraiton

```ini
CONSTANT_DELAY=300000
```

## Usage

```py linenums="1" title="error-strategy-example.py"
import asyncio
from rabbit import AioRabbitClient, Subscribe, fibo
from rabbit.job import async_echo_job

loop = asyncio.get_event_loop()

client = AioRabbitClient()
loop.create_task(
    client.persistent_connect(
        host='localhost',
        port=5672,
        login='guest',
        password='guest',
        channel_max=2047
    )
)


consumer = Subscribe(
    client=client,
    concurrent=2,
    delay_strategy=fibo, # here can you change for any valid option: [fibo, expo, constant]
    task=async_echo_job
)
loop.create_task(consumer.configure())
```
