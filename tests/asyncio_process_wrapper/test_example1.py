import asyncio

from asyncio_process_wrapper.example1 import run_process


def test_run_process():
    async def _run_process():
        result = await run_process("abc", "def")
        assert result == "some result value"

    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(_run_process())
