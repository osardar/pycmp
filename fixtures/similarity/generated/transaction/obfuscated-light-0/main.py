class _v8fc8ddedf504:
 def __init__(self, _v46070de93fe0):
  self.values = _v46070de93fe0
  self.saved = list(_v46070de93fe0)
 def __enter__(self):
  return self.values
 def __exit__(self, _va162420cd775, _vae6f00f3c445, _va27635227d59):
  if _va162420cd775 is not None:
   self.values[:] = self.saved
  return _va162420cd775 is ValueError
def run(payload):
 _v46070de93fe0 = list(payload['values'])
 with _v8fc8ddedf504(_v46070de93fe0) as _vc2536f58acd3:
  _vc2536f58acd3.append(9)
  if payload['rollback']:
   raise ValueError('rollback')
 return _v46070de93fe0
