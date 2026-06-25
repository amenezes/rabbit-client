## **Why should I use rabbit-client?**

`rabbit-client` provides a high level abstraction to consume and produce asynchronous events with some level of warranty that events won't be lost in case of failures.

!!! info "v4.0.0 migration"
    Starting with version 4.0.0, the transport layer was migrated from the archived `aioamqp` to the actively maintained `aio-pika` / `aiormq`. The public API changed: `persistent_connect()` + `register()` were replaced by `connect()` + `channel()` + `configure()`. See the [releases page](https://github.com/amenezes/rabbit-client/releases) for details.

## **Why use rabbit-client instead of aio-pika directly?**

`aio-pika` is the low-level async AMQP transport — you declare exchanges, queues, binds, and handle ack/nack manually. `rabbit-client` builds on top of it to provide:

- **DLX + retry out of the box**: on task failure, the message is automatically routed to a Dead Letter Exchange and retried after a configurable delay (`constant`, `expo`, `fibo`). With raw `aio-pika` you'd need to declare the DLX topology and handle retry logic yourself (~80 lines).
- **Declarative topology** via `Exchange` and `Queue` value objects with built-in validation.
- **Integrated ack/DLQ** in `Subscribe`: success acks, failure acks the original *and* sends a copy to DLX — a single error-handling pattern.
- **CLI** (`rabbit consumer` / `rabbit send-event`) for ad-hoc testing.

If you need fine-grained control (custom ack strategies, transaction channels, `mandatory` publishes), use `aio-pika` directly. `rabbit-client` exposes the underlying `aio_pika` objects so you can drop down when needed.

## **What type of job can I use?**

The `Subscribe` class uses a `task` that's nothing more than an awaitable. This will be executed when an event is received by the queue, so you can use a task to process IO or CPU bound jobs via [`asyncio.to_thread`](https://docs.python.org/3/library/asyncio-task.html#asyncio.to_thread) (Python ≥ 3.9).

```python
import asyncio
from rabbit import Subscribe

async def io_task(message):
    data = message.body.decode()
    # async HTTP call, DB query, etc.

def cpu_task(message):
    # heavy computation — runs in a thread pool
    return process(message.body)

subscribe = Subscribe(task=io_task)

# For CPU-bound work, wrap with asyncio.to_thread:
async def cpu_bound_task(message):
    await asyncio.to_thread(cpu_task, message)
```

## **Why use Dead Letter Exchange?**

A DLQ will assist you to not lose an event that fails for some reason. So if somehow the task fails, raising any kind of exception, the event will be sent to the DLQ and after some delay defined by the `rabbit-client` strategy it will be back in the main queue so that the application can try to process it again.

- [When and how to use the RabbitMQ Dead Letter Exchange](https://www.cloudamqp.com/blog/when-and-how-to-use-the-rabbitmq-dead-letter-exchange.html)

## **How optimize concurrent jobs?**

Just increase the value of `concurrent` attribute in the `Subscribe`. This value is passed directly to `channel.set_qos(prefetch_count=N)`, controlling how many messages the broker delivers at once.

```python
# Process up to 5 messages concurrently
subscribe = Subscribe(task=my_task, concurrent=5)
```

However if the job consists of [CPU bound](https://en.wikipedia.org/wiki/CPU-bound) or long running tasks workloads it's a good choice to decrease the value.

- [How to Optimize the RabbitMQ Prefetch Count](https://www.cloudamqp.com/blog/how-to-optimize-the-rabbitmq-prefetch-count.html)

## **Does rabbit-client support publisher-confirms?**

Yes — publisher confirms are enabled by default on every channel by `aio-pika`. Unlike v3.x, there is no `publish_confirms` field on the `Publish` class; confirms are handled transparently. For advanced use cases (e.g., disabling confirms), use the aio-pika API directly.

Check these links:

- [Consumer Acknowledgements and Publisher Confirms](https://www.rabbitmq.com/confirms.html#publisher-confirms)
- [Introducing Publisher Confirms](https://blog.rabbitmq.com/posts/2011/02/introducing-publisher-confirms)

## **How does connection recovery work?**

`rabbit-client` delegates to `aio_pika.connect_robust()`, which maintains a background reconnection loop. After any network interruption it:

1. Re-establishes the TCP connection
2. Automatically restores all declared exchanges, queues, and bindings
3. Re-registers active consumers

No application-level watchers or polling is needed. By default, reconnection is attempted every 5 seconds. The first connection attempt fails immediately (`fail_fast=True`), so you know right away if the broker is unreachable at startup.

## **How do I gracefully shut down a consumer?**

The examples in the documentation use `asyncio.Event().wait()` as a simple "run forever" pattern. For production, handle OS signals:

```python
import asyncio
import signal

from rabbit import AioRabbitClient, Subscribe


async def main():
    client = AioRabbitClient()
    await client.connect(host="localhost", port=5672)
    channel = await client.channel()

    subscribe = Subscribe(task=my_task)
    await subscribe.configure(channel)

    stop = asyncio.Event()

    def shutdown():
        stop.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown)

    await stop.wait()
    await client.close()
```

## **Can I access aio-pika objects directly?**

Yes. `rabbit-client` is a thin layer — all internal broker proxies are accessible:

```python
subscribe._channel        # aio_pika.abc.AbstractChannel
subscribe._main_exchange  # aio_pika.abc.AbstractExchange
subscribe._main_queue     # aio_pika.abc.AbstractQueue
```

This means you can use advanced `aio-pika` features (e.g., `exchange.publish()` with custom headers, `queue.purge()`, `queue.declare_queue()` with custom arguments) without leaving the library.

## **How do I customize the DLX delay strategy?**

Pass a pre-configured callable via `Subscribe(delay_strategy=...)`:

```python
from functools import partial
from rabbit import Subscribe, expo

subscribe = Subscribe(
    task=my_task,
    delay_strategy=partial(expo, delay=60000, base=3, max_delay=1800000),
)
```

See the [delay strategies](./error_strategies.md) page for `constant`, `expo`, and `fibo` details.

## **What happens if the retry queue (`.dlq`) is full?**

The original message is acknowledged (acked) before the DLX copy is published. If the DLX publish fails (queue full, broker unavailable), the message is **lost** — it won't return to the main queue. The library logs a warning:

```
DLQ send failed in error path
```

**Mitigation**: monitor the `.dlq` queue depth and set up alerts. If messages accumulate in `.dlq`, the TTL-based retry loop may be too aggressive for the failure rate. Consider:

- Increasing the base delay (`delay_strategy`)
- Using a capped `max_delay` with `expo`/`fibo`
- Setting a queue length limit on the `.dlq` queue and handling overflow separately
