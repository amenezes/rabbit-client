# CLI

## Installing dependencies

```bash
pip install 'rabbit-client[cli]'
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
  -c, --concurrent INTEGER  How many concurrent events to process.  [default:
                            1]
  -x, --exchange TEXT       Exchange name.  [default: default.in.exchange]
  -t, --type TEXT           Exchange topic type name.  [default: topic]
  -k, --key TEXT            Exchange topic key.  [default: #]
  -q, --queue TEXT          Queue name.  [default: default.subscribe.queue]
  --chaos                   Enable chaos mode. Raise random Exception to test
                            DLX mechanism.
  -h, --help                Show this message and exit.
```

#### chaos mode 🔥

```bash
python -m rabbit consumer --chaos
```

### producer/send-event

Send events to message broker.

```bash
python -m rabbit send-event data.json
```

> `PAYLOAD` argument can be some `file` or `directory` with a list of json files.

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
  --verify              Verify ssl certificate?
  --channels INTEGER    Channel max.  [default: 1]
  -v, --verbose         Extend output info.
  -h, --help            Show this message and exit.
```
