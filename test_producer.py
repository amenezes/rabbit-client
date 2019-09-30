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
