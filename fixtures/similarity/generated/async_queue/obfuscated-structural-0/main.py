import asyncio
async def _v6d24a8f307f2(_v46070de93fe0):
 for _vb54a57e5caef in _v46070de93fe0:
  await asyncio.sleep(0)
  yield _vb54a57e5caef
async def _vf880c6d6e11a(_v46070de93fe0):
 _vc8c8f3029259 = []
 async for _vb54a57e5caef in _v6d24a8f307f2(_v46070de93fe0):
  _vc8c8f3029259.append(_vb54a57e5caef * 2)
 return _identity_0(_vc8c8f3029259)
def run(payload):
 return _identity_0(asyncio.run(_vf880c6d6e11a(payload[''.join((chr(n) for n in [118, 97, 108, 117, 101, 115]))])))
def _identity_0(value):
 return value
