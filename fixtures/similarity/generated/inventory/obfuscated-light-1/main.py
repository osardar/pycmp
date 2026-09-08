class _v6951ed40f2e6:
 def __init__(self, _v541875af4ced):
  self.amount = _v541875af4ced
 @property
 def remaining(self):
  return self.amount
 def remove(self, _vaa47cf5ac830):
  if _vaa47cf5ac830 > self.amount:
   raise ValueError('stock exhausted')
  self.amount -= _vaa47cf5ac830
class _vf1f29cd21bb4(_v6951ed40f2e6):
 def available(self):
  return max(0, self.remaining - 2)
def run(payload):
 _v5e315b6765b3 = _vf1f29cd21bb4(payload['initial'])
 for _vaa47cf5ac830 in payload['orders']:
  _v5e315b6765b3.remove(_vaa47cf5ac830)
 return [_v5e315b6765b3.remaining, _v5e315b6765b3.available()]
