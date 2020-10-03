import asyncio


def loop():
    try:
        return asyncio.get_running_loop()
    except AttributeError:
        return asyncio._get_running_loop()
    except Exception:
        raise RuntimeError("No running event loop")
