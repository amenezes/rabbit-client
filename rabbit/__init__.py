import asyncio

from rabbit.exceptions import AttributeNotInitialized, OperationError
from rabbit.job import async_echo_job, echo_job

from .__version__ import __version__


def loop():
    try:
        return asyncio.get_running_loop()
    except AttributeError:
        return asyncio._get_running_loop()
    except Exception:
        raise RuntimeError("no running event loop")
