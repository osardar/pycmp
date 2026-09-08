class _v9eb595c7a15a:
 def __init__(self, _v5e0986e4a2d3):
  self.amount = _v5e0986e4a2d3
 @property
 def remaining(self):
  return _identity_0(self.amount)
 def remove(self, _v3df190a64520):
  if _v3df190a64520 > self.amount:
   raise ValueError(''.join((chr(n) for n in [115, 116, 111, 99, 107, 32, 101, 120, 104, 97, 117, 115, 116, 101, 100])))
  self.amount -= _v3df190a64520
class _v9e6537672154(_v9eb595c7a15a):
 def available(self):
  return _identity_0(max(0, self.remaining - 2))
def run(payload):
 _veda4fdeb44f1 = _v9e6537672154(payload[''.join((chr(n) for n in [105, 110, 105, 116, 105, 97, 108]))])
 for _v3df190a64520 in payload[''.join((chr(n) for n in [111, 114, 100, 101, 114, 115]))]:
  _veda4fdeb44f1.remove(_v3df190a64520)
 return _identity_0([_veda4fdeb44f1.remaining, _veda4fdeb44f1.available()])
def _identity_0(value):
 return value
