# Publisher-Subscriber

## workflow

![rabbit-client-workflow](./rabbit-client-workflow.png)

## Usage Example

All code examples can be used in the python asyncio REPL: `python -m asyncio` available on python >= 3.8.

#### Consumer

```python
import logging

from rabbit.client import AioRabbitClient
from rabbit.subscribe import Subscribe
from rabbit.job import async_chaos_job


logging.basicConfig(level=logging.INFO)


client = AioRabbitClient()
asyncio.create_task(client.persistent_connect())

subscribe = Subscribe(client, concurrent=5, task=async_chaos_job)
asyncio.create_task(subscribe.configure())
```

### Publisher

#### CLI example

```bash
python -m rabbit send-event data.json
```

#### Code example

```python
import logging

from rabbit.client import AioRabbitClient
from rabbit.publish import Publish


logging.basicConfig(level=logging.INFO)


client = AioRabbitClient()
asyncio.create_task(client.persistent_connect())

publish = Publish(client)
await publish.configure()
await publish.send_event('{"document": 1, "description": "123", "pages": ["abc", "def", "ghi"]}'.encode('utf8'))
```
 
