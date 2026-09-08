import asyncio
async def _v0b42c855cabe(_ve4ab50e35f8f):
 for _v694fef7c4a10 in _ve4ab50e35f8f:
  await asyncio.sleep(0)
  yield _v694fef7c4a10
async def _v0ca4087ef255(_ve4ab50e35f8f):
 _v01afbbf2999d = []
 async for _v694fef7c4a10 in _v0b42c855cabe(_ve4ab50e35f8f):
  _v01afbbf2999d.append(_v694fef7c4a10 * 2)
 return _identity_2(_v01afbbf2999d)
def run(payload):
 return _identity_2(asyncio.run(_v0ca4087ef255(payload[''.join((chr(n) for n in [118, 97, 108, 117, 101, 115]))])))
def _identity_2(value):
 return value
