# Overview

**rabbit-client** has full support to use with async python applications following some best practices to delivery features like:  

- connection and reconnection management with broker;  
- automatic channel configuration;  
- automatic [Dead Letter Exchange](https://www.rabbitmq.com/dlx.html) configuration and use;  
- concurrent task execution powered by asyncio `[optional]`;
- [publisher confirms](https://www.rabbitmq.com/confirms.html#publisher-confirms) `[optional]`;
- automatic qos configuration;
- different strategies to delay error events.

## Setup

The main values expected to configure `rabbit-client` can be set via environment variables.

### Default values

```.env
# publisher - send_event method
PUBLISH_EXCHANGE_NAME=default.in.exchange
PUBLISH_ROUTING_KEY=#

# subscriber
SUBSCRIBE_EXCHANGE_NAME=default.in.exchange
SUBSCRIBE_EXCHANGE_TYPE=topic
SUBSCRIBE_TOPIC=#
SUBSCRIBE_QUEUE_NAME=default.subscribe.queue

# dlx
DLX_EXCHANGE_NAME=DLX
DLX_TYPE=direct

DLQ_EXCHANGE_NAME=dlqReRouter.default.in.exchange
DLQ_EXCHANGE_TYPE=default.subscribe.queue

# dlx strategies
## expo
EXPO_DELAY=300000
EXPO_BASE=2
EXPO_FACTOR=1
EXPO_MAX_DELAY=

## fibo
FIBO_DELAY=300000 # 5 minutes
FIBO_MAX_DELAY=86400000 # 1 day

## constant
CONSTANT_DELAY=300000 # 5 minutes
```
