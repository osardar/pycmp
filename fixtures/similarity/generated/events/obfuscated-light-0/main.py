def _ve44d121b8306(_v46070de93fe0, _vabb0bd0810b8):
 for _vacb28ecf9321 in range(0, len(_v46070de93fe0), _vabb0bd0810b8):
  yield _v46070de93fe0[_vacb28ecf9321:_vacb28ecf9321 + _vabb0bd0810b8]
def run(payload):
 _vc44ee822202b = (_vb54a57e5caef for _vb54a57e5caef in payload['values'] if _vb54a57e5caef >= 0)
 return [sum(_vabed7dd2718f) for _vabed7dd2718f in _ve44d121b8306(list(_vc44ee822202b), 2)]
