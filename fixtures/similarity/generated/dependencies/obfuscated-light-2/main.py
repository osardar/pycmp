def _v5266d1b276c1(_v713b052f9db8, _v5ac00db084fa, _v2c195281bb4c, _v01afbbf2999d):
 if _v713b052f9db8 in _v2c195281bb4c:
  return
 _v2c195281bb4c.add(_v713b052f9db8)
 for _v9366724d0e57 in _v5ac00db084fa.get(_v713b052f9db8, []):
  _v5266d1b276c1(_v9366724d0e57, _v5ac00db084fa, _v2c195281bb4c, _v01afbbf2999d)
 _v01afbbf2999d.append(_v713b052f9db8)
def run(payload):
 _v01afbbf2999d = []
 _v5266d1b276c1(payload['root'], payload['graph'], set(), _v01afbbf2999d)
 return _v01afbbf2999d
