import logging

import attr

from rabbit.exchange import Exchange


logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True, frozen=True)
class Event:

    channel = attr.ib()
    payload = attr.ib(
        type=bytes,
        validator=attr.validators.instance_of(bytes)
    )
    exchange = attr.ib(
        type=Exchange,
        default=None,
        validator=attr.validators.optional(
            validator=attr.validators.instance_of(Exchange)
        )
    )
    properties = attr.ib(
        type=dict,
        default={},
        validator=attr.validators.instance_of(dict)
    )
    envelope = attr.ib(
        default=None
    )
    delay = attr.ib(
        type=int,
        default=5000,
        validator=attr.validators.instance_of(int)
    )
    requeue = attr.ib(
        type=bool,
        default=False,
        validator=attr.validators.instance_of(bool)
    )
    timeout = attr.ib(
        type=int,
        default=5000,
        validator=attr.validators.instance_of(int)
    )
    headers = attr.ib(
        type=dict,
        default={
            'x-delay': delay
        },
        validator=attr.validators.instance_of(dict)
    )

    async def publish(self, routing_key):
        await self.channel.publish(
            payload=self.payload,
            exchange_name=self.exchange.name,
            routing_key=routing_key,
            properties=self.properties
        )

    async def reject(self):
        await self.channel.basic_client_nack(
            delivery_tag=self.envelope.delivery_tag,
            requeue=self.requeue
        )

    async def ack(self):
        await self.channel.basic_client_ack(
            delivery_tag=self.envelope.delivery_tag
        )

    # async def get_timeout(headers, delay=5000):
    #     if (headers is not None) and ('x-delay' in headers):
    #         delay = headers['x-delay']
    #     return int(delay) * 5
