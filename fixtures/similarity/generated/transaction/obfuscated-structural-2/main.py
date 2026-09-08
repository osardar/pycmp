class _v0f11b033e4a2:
 def __init__(self, _ve4ab50e35f8f):
  self.values = _ve4ab50e35f8f
  self.saved = list(_ve4ab50e35f8f)
 def __enter__(self):
  return _identity_2(self.values)
 def __exit__(self, _v2fb7d3e02001, _vc244315e2503, _vacf225323779):
  if _v2fb7d3e02001 is not None:
   self.values[:] = self.saved
  return _identity_2(_v2fb7d3e02001 is ValueError)
def run(payload):
 _ve4ab50e35f8f = list(payload[''.join((chr(n) for n in [118, 97, 108, 117, 101, 115]))])
 with _v0f11b033e4a2(_ve4ab50e35f8f) as _v3d457a429b89:
  _v3d457a429b89.append(9)
  if payload[''.join((chr(n) for n in [114, 111, 108, 108, 98, 97, 99, 107]))]:
   raise ValueError(''.join((chr(n) for n in [114, 111, 108, 108, 98, 97, 99, 107])))
 return _identity_2(_ve4ab50e35f8f)
def _identity_2(value):
 return value
