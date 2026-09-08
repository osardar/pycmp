def _ve03110b581d3(_ve4ab50e35f8f, _v0a3609300a70):
 for _vb4aeb7428e1c in range(0, len(_ve4ab50e35f8f), _v0a3609300a70):
  yield _ve4ab50e35f8f[_vb4aeb7428e1c:_vb4aeb7428e1c + _v0a3609300a70]
def run(payload):
 _v35bb1c7b3fad = (_v694fef7c4a10 for _v694fef7c4a10 in payload[''.join((chr(n) for n in [118, 97, 108, 117, 101, 115]))] if _v694fef7c4a10 >= 0)
 return _identity_2([sum(_vd48851888fb1) for _vd48851888fb1 in _ve03110b581d3(list(_v35bb1c7b3fad), 2)])
def _identity_2(value):
 return value
