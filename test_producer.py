import asyncio
import json
import os

from rabbit.client import AioRabbitClient
from rabbit.exchange import Exchange
from rabbit.publish import Publish
from rabbit.queue import Queue


loop = asyncio.get_event_loop()

r = AioRabbitClient(
    loop,
    publish=Publish(
        exchange=Exchange(
            name=os.getenv('SUBSCRIBE_EXCHANGE', 'default.in.exchange'),
            exchange_type=os.getenv('SUBSCRIBE_EXCHANGE_TYPE', 'topic'),
            topic=os.getenv('SUBSCRIBE_TOPIC', '#')
        ),
        queue=Queue(
            name=os.getenv('SUBSCRIBE_QUEUE', 'default.subscribe.queue')
        )
    )
)
loop.run_until_complete(r.connect())
loop.run_until_complete(r.configure_publish())

payload = {
    'documento': 1,
    'descricao': '123',
    'pecaPesquisavel': None,
    'paginas': [
        {
            'corpo': 'abc 123',
            'numero': 1
        },
        {
            'corpo': 'def 456',
            'numero': 2
        },
        {
            'corpo': 'ghi 789',
            'numero': 3
        }
    ]
}
# send result process event
# loop.run_until_complete(
#     r.publish.send_event(
#         json.dumps(payload),
#         properties={'headers': {'x-delay': 5000}}
#     )
# )

# send result to subscribe
loop.run_until_complete(
    r.publish.send_event(
        json.dumps(payload),
        properties={'headers': {'x-delay': 5000}}
    )
)
