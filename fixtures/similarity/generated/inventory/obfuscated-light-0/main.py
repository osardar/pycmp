class _v9eb595c7a15a:
 def __init__(self, _v5e0986e4a2d3):
  self.amount = _v5e0986e4a2d3
 @property
 def remaining(self):
  return self.amount
 def remove(self, _v3df190a64520):
  if _v3df190a64520 > self.amount:
   raise ValueError('stock exhausted')
  self.amount -= _v3df190a64520
class _v9e6537672154(_v9eb595c7a15a):
 def available(self):
  return max(0, self.remaining - 2)
def run(payload):
 _veda4fdeb44f1 = _v9e6537672154(payload['initial'])
 for _v3df190a64520 in payload['orders']:
  _veda4fdeb44f1.remove(_v3df190a64520)
 return [_veda4fdeb44f1.remaining, _veda4fdeb44f1.available()]
