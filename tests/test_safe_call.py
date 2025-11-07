import asyncio
import types

from utils.safe_call import safe_call_respond


class SyncHandler:
    def __init__(self):
        self.called = 0

    def respond(self, *args, **kwargs):
        self.called += 1
        return (args, kwargs)


class AsyncHandler:
    def __init__(self):
        self.called = 0

    async def respond(self, *args, **kwargs):
        self.called += 1
        await asyncio.sleep(0)
        return (args, kwargs)


def test_safe_call_sync():
    h = SyncHandler()
    out = safe_call_respond(h, 1, a=2)
    assert h.called == 1
    assert out == ((1,), {"a": 2})


def test_safe_call_async_runs():
    h = AsyncHandler()
    out = safe_call_respond(h, 3, b=4)
    # safe_call_respond should consume coroutine via asyncio.run if possible
    assert h.called == 1
    assert out == ((3,), {"b": 4})
