"""Python 3.5: coroutine composition."""
import asyncio

async def increment(value):
    await asyncio.sleep(0)
    return value + 1

async def pipeline(value):
    return await increment(await increment(value))
