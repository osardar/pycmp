import asyncio
async def _v0b42c855cabe(_ve4ab50e35f8f):
 for _v694fef7c4a10 in _ve4ab50e35f8f:
  await asyncio.sleep(0)
  yield _v694fef7c4a10
async def _v0ca4087ef255(_ve4ab50e35f8f):
 _v01afbbf2999d = []
 async for _v694fef7c4a10 in _v0b42c855cabe(_ve4ab50e35f8f):
  _v01afbbf2999d.append(_v694fef7c4a10 * 2)
 return _v01afbbf2999d
def run(payload):
 return asyncio.run(_v0ca4087ef255(payload['values']))
