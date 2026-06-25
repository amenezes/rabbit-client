"""Integration tests for Phase 1 — aio-pika client foundation."""

import asyncio

import aio_pika
import pytest

from rabbit.client import AioRabbitClient


@pytest.mark.integration
async def test_connect_and_close(amqp_url):
    client = AioRabbitClient()
    await client.connect(url=amqp_url)
    assert client.is_connected
    await client.close()
    assert not client.is_connected


@pytest.mark.integration
async def test_connect_with_kwargs(amqp_url):
    client = AioRabbitClient()
    await client.connect(
        host="localhost", port=5672, login="guest", password="guest", virtualhost="/"
    )
    assert client.is_connected
    await client.close()


@pytest.mark.integration
async def test_channel_creation(amqp_url):
    client = AioRabbitClient()
    await client.connect(url=amqp_url)
    channel = await client.channel()
    assert channel is not None
    assert not channel.is_closed
    await channel.close()
    await client.close()


@pytest.mark.integration
async def test_publish_and_consume(amqp_url):
    connection = await aio_pika.connect_robust(amqp_url)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("test_phase1_pubsub", exclusive=True)

        received = asyncio.Event()
        body_received = None

        async def handler(message: aio_pika.IncomingMessage):
            nonlocal body_received
            async with message.process():
                body_received = message.body
                received.set()

        await queue.consume(handler)

        await channel.default_exchange.publish(
            aio_pika.Message(b"hello-phase1"),
            routing_key="test_phase1_pubsub",
        )

        await asyncio.wait_for(received.wait(), timeout=5.0)
        assert body_received == b"hello-phase1"


@pytest.mark.integration
async def test_message_ack_after_successful_processing(amqp_url):
    connection = await aio_pika.connect_robust(amqp_url)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("test_phase1_ack", exclusive=True)

        received = asyncio.Event()

        async def handler(message: aio_pika.IncomingMessage):
            async with message.process():
                received.set()

        await queue.consume(handler)

        await channel.default_exchange.publish(
            aio_pika.Message(b"ack-me"),
            routing_key="test_phase1_ack",
        )

        await asyncio.wait_for(received.wait(), timeout=5.0)

        # After ack, the queue should be empty
        await asyncio.sleep(0.3)
        assert queue.declaration_result.message_count == 0


@pytest.mark.integration
async def test_prefetch_count_limits_concurrent_delivery(amqp_url):
    connection = await aio_pika.connect_robust(amqp_url)
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)
        queue = await channel.declare_queue("test_phase1_prefetch", exclusive=True)

        processing = 0
        max_concurrent = 0
        all_done = asyncio.Event()
        message_count = 5

        async def handler(message: aio_pika.IncomingMessage):
            nonlocal processing, max_concurrent
            processing += 1
            max_concurrent = max(max_concurrent, processing)
            await asyncio.sleep(0.2)
            async with message.process():
                pass
            processing -= 1
            if message.body == f"msg{message_count - 1}".encode():
                all_done.set()

        await queue.consume(handler)

        for i in range(message_count):
            await channel.default_exchange.publish(
                aio_pika.Message(f"msg{i}".encode()),
                routing_key="test_phase1_prefetch",
            )

        await asyncio.wait_for(all_done.wait(), timeout=10.0)
        assert max_concurrent == 1


@pytest.mark.integration
async def test_client_context_manager(amqp_url):
    async with AioRabbitClient() as client:
        await client.connect(url=amqp_url)
        assert client.is_connected
    assert not client.is_connected
