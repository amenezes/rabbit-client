# CLI

## Installing dependencies

```bash
uv pip install 'rabbit-client[cli]'
```

## Usage

```bash
python -m rabbit
```

```bash
# expected output
Usage: python -m rabbit [OPTIONS] COMMAND [ARGS]...

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  consumer    Start a consumer sample application 📩
  send-event  Send a sample message 📤 to Consumer or PollingPublisher
```

### consumer

```bash
python -m rabbit consumer -h
```

```bash
# expected output
Usage: python -m rabbit consumer [OPTIONS]

  Start a consumer sample application 📩

Options:
  --host TEXT               RabbitMQ hostname.  [default: localhost]
  --port INTEGER            RabbitMQ port.  [default: 5672]
  --login TEXT              RabbitMQ username.  [default: guest]
  --password TEXT           RabbitMQ password.  [default: guest]
  -c, --concurrent INTEGER  How many concurrent events to process.  [default: 1]
  -x, --exchange TEXT       Exchange name.  [default: default.in.exchange]
  -t, --type TEXT           Exchange topic type name.  [default: topic]
  -k, --key TEXT            Exchange topic key.  [default: #]
  -q, --queue TEXT          Queue name.  [default: default.subscribe.queue]
  --chaos                   Enable chaos mode. Raise random Exception to test
                            DLX mechanism.
  -v, --verbose             Extend output info.
  -h, --help                Show this message and exit.
```

#### chaos mode 🔥

```bash
python -m rabbit consumer --chaos
```

### producer/send-event

Send events to the message broker.

```bash
python -m rabbit send-event data.json
```

> `PAYLOAD` argument can be a `file` or `directory` with a list of json files.

```bash
# expected output
Usage: python -m rabbit send-event [OPTIONS] PAYLOAD

  Send a sample message 📤 to Consumer or PollingPublisher

Options:
  -e, --events INTEGER  How many events to send.  [default: 1]
  -x, --exchange TEXT   Exchange name.  [default: default.in.exchange]
  -k, --key TEXT        Exchange topic key.  [default: #]
  --host TEXT           RabbitMQ host.  [default: localhost]
  --port INTEGER        RabbitMQ port.  [default: 5672]
  --login TEXT          RabbitMQ login.  [default: guest]
  --password TEXT       RabbitMQ password.  [default: guest]
  --ssl                 Enable rabbit ssl connection.
  -v, --verbose         Extend output info.
  -h, --help            Show this message and exit.
```

!!! warning "Removed in v4.0.0"
    The `--verify` and `--channels` options available in v3.x have been removed. SSL certificate verification and channel multiplexing are now handled by `aio-pika` / `connect_robust` natively.
