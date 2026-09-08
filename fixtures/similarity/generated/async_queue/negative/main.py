import asyncio

async def stream(values):
    for value in values:
        await asyncio.sleep(0)
        yield value

async def collect(values):
    output = []
    async for value in stream(values):
        output.append(value + 2)
    return output

def run(payload):
    return asyncio.run(collect(payload['values']))
