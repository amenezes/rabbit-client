# Polling Publisher

> From the version 1.x this feature is supported out-of-box.

![rabbit-client-workflow-polling](./rabbit-client-workflow-polling.png)

## Pattern

> [https://microservices.io/patterns/data/polling-publisher.html](https://microservices.io/patterns/data/polling-publisher.html)

## Usage Example

### Subscribe & Polling Publisher

```python
import asyncio
import logging

from rabbit import AioRabbitClient, Publish
from rabbit.exchange import Exchange


logging.getLogger().setLevel(logging.DEBUG)

   
client = AioRabbitClient()
asyncio.create_task(client.persistent_connect())

publish = Publish(client=client)
loop.create_task(publish.configure())

class MyRepo:
    def __init__(self, publish, db):
        self._publish = publish
        self._db = db
    
    async def start_polling():
        while True:
            await asyncio.sleep(10)
            # do some work here and retrieve database event data.
            await self._publish.send_event(event)

repo = MyRepo(publish, DB())
asyncio.create_task(repo.start_polling())
```
