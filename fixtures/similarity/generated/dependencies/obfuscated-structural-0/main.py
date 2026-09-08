def _v3f5de837cecf(_ve387fedcd9f6, _v62e603fd712c, _v2cf4a3179cec, _vc8c8f3029259):
 if _ve387fedcd9f6 in _v2cf4a3179cec:
  return
 _v2cf4a3179cec.add(_ve387fedcd9f6)
 for _v3877ae64b76f in _v62e603fd712c.get(_ve387fedcd9f6, []):
  _v3f5de837cecf(_v3877ae64b76f, _v62e603fd712c, _v2cf4a3179cec, _vc8c8f3029259)
 _vc8c8f3029259.append(_ve387fedcd9f6)
def run(payload):
 _vc8c8f3029259 = []
 _v3f5de837cecf(payload[''.join((chr(n) for n in [114, 111, 111, 116]))], payload[''.join((chr(n) for n in [103, 114, 97, 112, 104]))], set(), _vc8c8f3029259)
 return _identity_0(_vc8c8f3029259)
def _identity_0(value):
 return value
