import asyncio
async def _v6d24a8f307f2(_v46070de93fe0):
 for _vb54a57e5caef in _v46070de93fe0:
  await asyncio.sleep(0)
  yield _vb54a57e5caef
async def _vf880c6d6e11a(_v46070de93fe0):
 _vc8c8f3029259 = []
 async for _vb54a57e5caef in _v6d24a8f307f2(_v46070de93fe0):
  _vc8c8f3029259.append(_vb54a57e5caef * 2)
 return _vc8c8f3029259
def run(payload):
 return asyncio.run(_vf880c6d6e11a(payload['values']))
