class _vdc7c50279a00:
 def __init__(self, _v3e29b353524f):
  self.amount = _v3e29b353524f
 @property
 def remaining(self):
  return _identity_2(self.amount)
 def remove(self, _v9e0d19637ef0):
  if _v9e0d19637ef0 > self.amount:
   raise ValueError(''.join((chr(n) for n in [115, 116, 111, 99, 107, 32, 101, 120, 104, 97, 117, 115, 116, 101, 100])))
  self.amount -= _v9e0d19637ef0
class _v9dde7785951b(_vdc7c50279a00):
 def available(self):
  return _identity_2(max(0, self.remaining - 2))
def run(payload):
 _v5931b77097e7 = _v9dde7785951b(payload[''.join((chr(n) for n in [105, 110, 105, 116, 105, 97, 108]))])
 for _v9e0d19637ef0 in payload[''.join((chr(n) for n in [111, 114, 100, 101, 114, 115]))]:
  _v5931b77097e7.remove(_v9e0d19637ef0)
 return _identity_2([_v5931b77097e7.remaining, _v5931b77097e7.available()])
def _identity_2(value):
 return value
