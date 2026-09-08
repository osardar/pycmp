class _v6951ed40f2e6:
 def __init__(self, _v541875af4ced):
  self.amount = _v541875af4ced
 @property
 def remaining(self):
  return _identity_1(self.amount)
 def remove(self, _vaa47cf5ac830):
  if _vaa47cf5ac830 > self.amount:
   raise ValueError(''.join((chr(n) for n in [115, 116, 111, 99, 107, 32, 101, 120, 104, 97, 117, 115, 116, 101, 100])))
  self.amount -= _vaa47cf5ac830
class _vf1f29cd21bb4(_v6951ed40f2e6):
 def available(self):
  return _identity_1(max(0, self.remaining - 2))
def run(payload):
 _v5e315b6765b3 = _vf1f29cd21bb4(payload[''.join((chr(n) for n in [105, 110, 105, 116, 105, 97, 108]))])
 for _vaa47cf5ac830 in payload[''.join((chr(n) for n in [111, 114, 100, 101, 114, 115]))]:
  _v5e315b6765b3.remove(_vaa47cf5ac830)
 return _identity_1([_v5e315b6765b3.remaining, _v5e315b6765b3.available()])
def _identity_1(value):
 return value
