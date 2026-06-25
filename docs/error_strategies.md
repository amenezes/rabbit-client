## Delay strategies

- [Scheduling Messages with RabbitMQ](https://blog.rabbitmq.com/posts/2015/04/scheduling-messages-with-rabbitmq)

### expo

Exponential backoff time, inspired in the great library [backoff](https://github.com/litl/backoff).

By default a cycle with 3 iterations will produce:

```txt linenums="1"
600000  # 10 minutes
1200000 # 20 minutes
2400000 # 40 minutes
```

#### signature

```python
def expo(
    headers: dict | None,
    delay: int = 300000,
    base: int = 2,
    factor: int = 1,
    max_delay: int | None = None,
) -> int:
```

!!! warning "Breaking change in v4.0.0"
    Environment variables (`EXPO_DELAY`, `EXPO_BASE`, `EXPO_FACTOR`, `EXPO_MAX_DELAY`) are **no longer read** by the library. To customize delay parameters, pass a pre-configured callable via `Subscribe(delay_strategy=...)`:

    ```python
    from functools import partial
    from rabbit import expo

    subscribe = Subscribe(
        task=my_task,
        delay_strategy=partial(expo, delay=60000, base=3, max_delay=1800000),
    )
    ```

### fibo

Incremental delay by minute.

By default a cycle with 3 iterations will produce:

```txt linenums="1"
1. 360000  # 6 minutes
2. 420000  # 7 minutes
3. 480000  # 8 minutes
```

#### signature

```python
def fibo(
    headers: dict | None,
    delay: int = 300000,
    max_delay: int = 86400000,
) -> int:
```

!!! warning "Breaking change in v4.0.0"
    Environment variables (`FIBO_DELAY`, `FIBO_MAX_DELAY`) are **no longer read**. Use `functools.partial` to customize:

    ```python
    from functools import partial
    from rabbit import fibo

    subscribe = Subscribe(
        task=my_task,
        delay_strategy=partial(fibo, delay=120000, max_delay=43200000),
    )
    ```

### constant

Constant time.

By default a cycle with 3 iterations will produce:

```txt linenums="1"
300000  # 5 minutes
300000  # 5 minutes
300000  # 5 minutes
```

> **constant** strategy is the default option for Subscribe.

#### signature

```python
def constant(headers: dict | None, delay: int = 300000) -> int:
```

!!! warning "Breaking change in v4.0.0"
    Environment variable `CONSTANT_DELAY` is **no longer read**. Customize via:

    ```python
    from functools import partial
    from rabbit import constant

    subscribe = Subscribe(
        task=my_task,
        delay_strategy=partial(constant, delay=120000),
    )
    ```

## Usage

```py linenums="1" title="error-strategy-example.py"
import asyncio

from rabbit import AioRabbitClient, Exchange, Queue, Subscribe, fibo
from rabbit.job import async_echo_job


async def main():
    client = AioRabbitClient()
    await client.connect(host="localhost", port=5672)
    channel = await client.channel()

    subscribe = Subscribe(
        task=async_echo_job,
        exchange=Exchange(name="default.in.exchange", exchange_type="topic", topic="#"),
        queue=Queue(name="default.subscribe.queue"),
        concurrent=2,
        delay_strategy=fibo,  # or: partial(fibo, delay=60000, max_delay=1800000)
    )
    await subscribe.configure(channel)
    await asyncio.Event().wait()


asyncio.run(main())
```
