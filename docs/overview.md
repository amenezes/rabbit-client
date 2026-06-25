# Overview

**rabbit-client** has full support to use with async python applications following some best practices to delivery features like:  

- connection and reconnection management with broker (powered by `aio-pika`'s `connect_robust`);
- automatic channel configuration;
- automatic [Dead Letter Exchange](https://www.rabbitmq.com/dlx.html) configuration and use;
- concurrent task execution powered by asyncio `[optional]`;
- automatic qos configuration;
- different strategies to delay error events.

!!! info "Publisher confirms"
    Publisher confirms are enabled by default by `aio-pika` on every channel. No explicit configuration is needed.

## Setup

Configuration is done via CLI flags (with documented defaults) or programmatically via `Exchange`, `Queue`, and `Subscribe` parameters.

### Removed in v4.0.0

The following environment variables were read by v3.x but are **no longer consulted** by v4.0.0:

| Env var | Replacement |
|---------|-------------|
| `SUBSCRIBE_EXCHANGE_NAME` | `--exchange` flag (default: `default.in.exchange`) |
| `SUBSCRIBE_EXCHANGE_TYPE` | `--type` flag (default: `topic`) |
| `SUBSCRIBE_TOPIC` | `--key` flag (default: `#`) |
| `SUBSCRIBE_QUEUE_NAME` | `--queue` flag (default: `default.subscribe.queue`) |
| `PUBLISH_EXCHANGE_NAME` | `--exchange` flag (default: `default.in.exchange`) |
| `PUBLISH_ROUTING_KEY` | `--key` flag (default: `#`) |
| `DLX_EXCHANGE_NAME` | DLX exchange name is hardcoded as `"DLX"` |
| `DLX_TYPE` | Hardcoded as `"direct"` |
| `DLQ_EXCHANGE_NAME` | Auto-generated from exchange name (`dlqReRouter.{exchange_name}`) |
| `DLQ_EXCHANGE_TYPE` | Hardcoded as `"topic"` |
| `EXPO_DELAY`, `EXPO_BASE`, `EXPO_FACTOR`, `EXPO_MAX_DELAY` | Use `functools.partial(expo, delay=..., ...)` via `Subscribe(delay_strategy=...)` |
| `FIBO_DELAY`, `FIBO_MAX_DELAY` | Use `functools.partial(fibo, delay=..., ...)` via `Subscribe(delay_strategy=...)` |
| `CONSTANT_DELAY` | Use `functools.partial(constant, delay=...)` via `Subscribe(delay_strategy=...)` |
