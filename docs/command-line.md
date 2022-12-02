# CLI

## Installing dependencies

```bash
pip install 'rabbit-client[cli]'
```

## Usage

```bash
Rabbit Client version 2.0.0

USAGE
  rabbit-client [-h] [-q] [-v [<...>]] [-V] [--ansi] [--no-ansi] [-n] <command> [<arg1>] ... [<argN>]

ARGUMENTS
  <command>              The command to execute
  <arg>                  The arguments of the command

GLOBAL OPTIONS
  -h (--help)            Display this help message
  -q (--quiet)           Do not output any message
  -v (--verbose)         Increase the verbosity of messages: "-v" for normal output, "-vv" for more
                         verbose output and "-vvv" for debug
  -V (--version)         Display this application version
  --ansi                 Force ANSI output
  --no-ansi              Disable ANSI output
  -n (--no-interaction)  Do not ask any interactive question

AVAILABLE COMMANDS
  consumer               Start a consumer sample application 📥
  help                   Display the manual of a command
  send-event             Send a sample message 📨 to Consumer or PollingPublisher
```

### consumer

```python
USAGE
  rabbit-client consumer [-c <...>] [-x <...>] [-t <...>] [-k <...>] [-f <...>] [<chaos>]

ARGUMENTS
  <chaos>                enable chaos mode. Raise random Exception to test DLX mechanism.

OPTIONS
  -c (--concurrent)      concurrent events to process. (default: "1")
  -x (--exchange)        exchange name. (default: "default.in.exchange")
  -t (--type)            exchange topic type name. (default: "topic")
  -k (--key)             exchange topic key. (default: "#")
  -f (--queue)           queue name. (default: "default.subscribe.queue")

GLOBAL OPTIONS
  -h (--help)            Display this help message
  -q (--quiet)           Do not output any message
  -v (--verbose)         Increase the verbosity of messages: "-v" for normal output, "-vv" for more
                         verbose output and "-vvv" for debug
  -V (--version)         Display this application version
  --ansi                 Force ANSI output
  --no-ansi              Disable ANSI output
  -n (--no-interaction)  Do not ask any interactive question
```

#### chaos mode

```bash
python -m rabbit consumer chaos
```

### producer/send-event

Send events to message broker.

```bash
USAGE
  rabbit-client send-event [-e <...>] [-x <...>] [-k <...>] [--host <...>] [--port <...>]
                           [--login <...>] [--pass <...>] [--ssl] [--verify] [--channels <...>]
                           <payload>

ARGUMENTS
  <payload>              payload file in json format.

OPTIONS
  -e (--events)          qtd events to send. (default: "1")
  -x (--exchange)        exchange name. (default: "default.in.exchange")
  -k (--key)             exchange topic key. (default: "#")
  --host                 rabbit hostname. (default: "localhost")
  --port                 rabbit port. (default: "5672")
  --login                rabbit login. (default: "guest")
  --pass                 rabbit password. (default: "guest")
  --ssl                  enable rabbit ssl connection.
  --verify               verify ssl certificate?.
  --channels             channel max. (default: "1")

GLOBAL OPTIONS
  -h (--help)            Display this help message
  -q (--quiet)           Do not output any message
  -v (--verbose)         Increase the verbosity of messages: "-v" for normal output, "-vv" for more
                         verbose output and "-vvv" for debug
  -V (--version)         Display this application version
  --ansi                 Force ANSI output
  --no-ansi              Disable ANSI output
  -n (--no-interaction)  Do not ask any interactive question
```
