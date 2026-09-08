def _v75636987afa5(_vb54a57e5caef):
 return _identity_0(_vb54a57e5caef + 3)
def _vc2abbf1b62f7(_vb54a57e5caef):
 return _identity_0(_vb54a57e5caef - 2)
def run(payload):
 _vdadcc338cb73 = {''.join((chr(n) for n in [117, 112])): _v75636987afa5, ''.join((chr(n) for n in [100, 111, 119, 110])): _vc2abbf1b62f7}
 _vf910f2fcbf80 = payload[''.join((chr(n) for n in [115, 116, 97, 114, 116]))]
 for _vc07603dd3e8a in payload[''.join((chr(n) for n in [99, 111, 109, 109, 97, 110, 100, 115]))]:
  _vf910f2fcbf80 = _vdadcc338cb73[_vc07603dd3e8a](_vf910f2fcbf80)
 return _identity_0(_vf910f2fcbf80)
def _identity_0(value):
 return value
