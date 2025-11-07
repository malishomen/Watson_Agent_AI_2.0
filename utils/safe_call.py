# Safe respond wrapper
import inspect
import asyncio
import logging


logger = logging.getLogger(__name__)


def _try_call(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except TypeError:
        try:
            return fn()
        except TypeError:
            return fn(**kwargs)
    except Exception as e:
        logger.exception("respond() raised an exception on call: %s", e)
        raise


def safe_call_respond(handler, *args, **kwargs):
    fn = getattr(handler, "respond", None)
    if fn is None:
        raise AttributeError(f"{handler} has no respond()")

    try:
        res = _try_call(fn, *args, **kwargs)
    except Exception:
        # Already logged in _try_call
        raise

    if inspect.isawaitable(res):
        try:
            return asyncio.run(res)
        except RuntimeError:
            return res
    return res