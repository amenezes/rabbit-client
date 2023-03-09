# Publisher-Subscriber

## workflow

![rabbit-client-workflow](./rabbit-client-workflow.png)

## Usage Example

All code examples can be used in the python asyncio REPL: `python -m asyncio` available on python >= 3.8.

#### Consumer

```python
import logging

from rabbit import AioRabbitClient, Subscribe
from rabbit.job import async_chaos_job


logging.basicConfig(level=logging.INFO)


client = AioRabbitClient()
asyncio.create_task(client.persistent_connect(host='localhost', port=5672))

subscribe = Subscribe(concurrent=5, task=async_chaos_job)
await client.register(subscribe)
```

### Publisher

#### CLI example

```bash
python -m rabbit send-event data.json
```

#### Code example

```python
import logging

from rabbit import AioRabbitClient, Publish


logging.basicConfig(level=logging.INFO)


client = AioRabbitClient()
asyncio.create_task(client.persistent_connect())

publish = Publish()
# publish = Publish(True) # for enable publish_confirms

await client.register(publish)
await publish.send_event('{"document": 1, "description": "123", "pages": ["abc", "def", "ghi"]}'.encode('utf8'))
```
 
