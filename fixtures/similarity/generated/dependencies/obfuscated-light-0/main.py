def _v3f5de837cecf(_ve387fedcd9f6, _v62e603fd712c, _v2cf4a3179cec, _vc8c8f3029259):
 if _ve387fedcd9f6 in _v2cf4a3179cec:
  return
 _v2cf4a3179cec.add(_ve387fedcd9f6)
 for _v3877ae64b76f in _v62e603fd712c.get(_ve387fedcd9f6, []):
  _v3f5de837cecf(_v3877ae64b76f, _v62e603fd712c, _v2cf4a3179cec, _vc8c8f3029259)
 _vc8c8f3029259.append(_ve387fedcd9f6)
def run(payload):
 _vc8c8f3029259 = []
 _v3f5de837cecf(payload['root'], payload['graph'], set(), _vc8c8f3029259)
 return _vc8c8f3029259
