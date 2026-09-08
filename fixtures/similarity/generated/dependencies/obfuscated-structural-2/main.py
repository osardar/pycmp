def _v5266d1b276c1(_v713b052f9db8, _v5ac00db084fa, _v2c195281bb4c, _v01afbbf2999d):
 if _v713b052f9db8 in _v2c195281bb4c:
  return
 _v2c195281bb4c.add(_v713b052f9db8)
 for _v9366724d0e57 in _v5ac00db084fa.get(_v713b052f9db8, []):
  _v5266d1b276c1(_v9366724d0e57, _v5ac00db084fa, _v2c195281bb4c, _v01afbbf2999d)
 _v01afbbf2999d.append(_v713b052f9db8)
def run(payload):
 _v01afbbf2999d = []
 _v5266d1b276c1(payload[''.join((chr(n) for n in [114, 111, 111, 116]))], payload[''.join((chr(n) for n in [103, 114, 97, 112, 104]))], set(), _v01afbbf2999d)
 return _identity_2(_v01afbbf2999d)
def _identity_2(value):
 return value
