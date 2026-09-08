class _vdc7c50279a00:
 def __init__(self, _v3e29b353524f):
  self.amount = _v3e29b353524f
 @property
 def remaining(self):
  return self.amount
 def remove(self, _v9e0d19637ef0):
  if _v9e0d19637ef0 > self.amount:
   raise ValueError('stock exhausted')
  self.amount -= _v9e0d19637ef0
class _v9dde7785951b(_vdc7c50279a00):
 def available(self):
  return max(0, self.remaining - 2)
def run(payload):
 _v5931b77097e7 = _v9dde7785951b(payload['initial'])
 for _v9e0d19637ef0 in payload['orders']:
  _v5931b77097e7.remove(_v9e0d19637ef0)
 return [_v5931b77097e7.remaining, _v5931b77097e7.available()]
