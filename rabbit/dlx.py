import asyncio
import logging
import os
from typing import Dict, Optional

from aioamqp.envelope import Envelope

import attr

from rabbit.client import AioRabbitClient
from rabbit.exchange import Exchange
from rabbit.queue import Queue


logging.getLogger(__name__).addHandler(logging.NullHandler())


@attr.s(slots=True)
class DLX:

    dlq_queue = attr.ib(
        type=Queue,
        validator=attr.validators.instance_of(Queue)
    )
    routing_key = attr.ib(
        type=str,
        validator=attr.validators.instance_of(str)
    )
    _client = attr.ib(
        type=Optional[AioRabbitClient],
        default=None,
        validator=attr.validators.optional(
            validator=attr.validators.instance_of(AioRabbitClient)
        )
    )
    dlx_exchange = attr.ib(
        type=Exchange,
        default=Exchange(
            name=os.getenv('DLX_EXCHANGE', 'DLX'),
            exchange_type=os.getenv('DLX_TYPE', 'direct')
        ),
        validator=attr.validators.instance_of(Exchange)
    )

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, client):
        if not isinstance(client, AioRabbitClient):
            raise ValueError('client must be AioRabbitClient instance.')
        self._client = client
        self._client.instances.append(self)

    async def ensure_client_is_valid(self) -> None:
        if not self._client:
            raise ValueError('To configure DLX a valid client must be set.')

    async def configure(self) -> None:
        await self.ensure_client_is_valid()
        await self._configure_exchange()
        await self._configure_queue()
        await self._configure_queue_bind()

    async def _configure_exchange(self) -> None:
        logging.debug(
            "Configuring DLX exchange: ["
            f"exchange_name: {self.dlx_exchange.name}] | "
            f"type_name: {self.dlx_exchange.exchange_type}"
            f" | durable: {self.dlx_exchange.durable}]"
        )
        await self._client.channel.exchange_declare(
            exchange_name=self.dlx_exchange.name,
            type_name=self.dlx_exchange.exchange_type,
            durable=self.dlx_exchange.durable
        )
        await asyncio.sleep(2)

    async def _configure_queue(self) -> None:
        queue_name = await self._ensure_endswith_dlq(
            self.dlq_queue.name
        )
        logging.debug(
            "Configuring DLX queue: ["
            f"queue_name: {queue_name}"
            f" | durable: {self.dlq_queue.durable} | "
            f"arguments: {self.dlq_queue.arguments}]"
        )
        await self._client.channel.queue_declare(
            queue_name=queue_name,
            durable=self.dlq_queue.durable,
            arguments=self.dlq_queue.arguments
        )

    async def _configure_queue_bind(self) -> None:
        queue_name = await self._ensure_endswith_dlq(
            self.dlq_queue.name
        )
        logging.debug(
            "Configuring DLX queue bind: ["
            f"exchange_name: {self.dlx_exchange.name}] | "
            f"type_name: {queue_name}"
            f" | routing_key: {self.routing_key}]"
        )

        await self._client.channel.queue_bind(
            exchange_name=self.dlx_exchange.name,
            queue_name=queue_name,
            routing_key=self.routing_key
        )

    async def _ensure_endswith_dlq(self, value: str) -> str:
        if not value.endswith('.dlq'):
            value = f'{value}.dlq'
        return value

    async def send_event(self, cause, body, envelope, properties) -> None:
        await self.ensure_client_is_valid()
        logging.error(f'Error to process event: {cause}')
        timeout = await self._get_timeout(properties.headers)
        properties = await self._get_properties(timeout, cause, envelope)
        queue_name = await self._ensure_endswith_dlq(
            self.dlq_queue.name
        )
        await self._client.channel.publish(
            body,
            self.dlx_exchange.name,
            queue_name,
            properties
        )

    async def _get_timeout(self, headers: Dict[str, int]) -> int:
        delay = 1000
        if (headers) and (headers.get('x-delay')):
            delay = headers.get('x-delay') or 5000
        return int(delay * 5)

    async def _get_properties(self,
                              timeout: int,
                              exception_message: str,
                              envelope: Envelope) -> Dict:
        properties = {
            'expiration': f'{timeout}',
            'headers': {
                'x-delay': f'{timeout}',
                'x-exception-message': f'{exception_message}',
                'x-original-exchange': f'{envelope.exchange_name}',
                'x-original-routingKey': f'{envelope.routing_key}'
            }
        }
        return properties
