import asyncio
import logging

from .__version__ import __version__

logger = logging.getLogger("rabbit-client")
logger.addHandler(logging.NullHandler())


def loop():
    try:
        return asyncio.get_running_loop()
    except AttributeError:
        return asyncio._get_running_loop()
    except Exception:
        raise RuntimeError("No running event loop")
