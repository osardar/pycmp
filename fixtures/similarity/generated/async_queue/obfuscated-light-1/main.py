import asyncio
async def _vad04af7f2c18(_v135daac92864):
 for _v8711e39e3d7d in _v135daac92864:
  await asyncio.sleep(0)
  yield _v8711e39e3d7d
async def _v7613b656b9a2(_v135daac92864):
 _v5cec851903a6 = []
 async for _v8711e39e3d7d in _vad04af7f2c18(_v135daac92864):
  _v5cec851903a6.append(_v8711e39e3d7d * 2)
 return _v5cec851903a6
def run(payload):
 return asyncio.run(_v7613b656b9a2(payload['values']))
