def _v75636987afa5(_vb54a57e5caef):
 return _vb54a57e5caef + 3
def _vc2abbf1b62f7(_vb54a57e5caef):
 return _vb54a57e5caef - 2
def run(payload):
 _vdadcc338cb73 = {'up': _v75636987afa5, 'down': _vc2abbf1b62f7}
 _vf910f2fcbf80 = payload['start']
 for _vc07603dd3e8a in payload['commands']:
  _vf910f2fcbf80 = _vdadcc338cb73[_vc07603dd3e8a](_vf910f2fcbf80)
 return _vf910f2fcbf80
