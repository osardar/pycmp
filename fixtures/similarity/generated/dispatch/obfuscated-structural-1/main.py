def _va7cd44d578a7(_v8711e39e3d7d):
 return _identity_1(_v8711e39e3d7d + 3)
def _v124fb42e5ef8(_v8711e39e3d7d):
 return _identity_1(_v8711e39e3d7d - 2)
def run(payload):
 _vdbbedb3807b3 = {''.join((chr(n) for n in [117, 112])): _va7cd44d578a7, ''.join((chr(n) for n in [100, 111, 119, 110])): _v124fb42e5ef8}
 _v5a626e8a3745 = payload[''.join((chr(n) for n in [115, 116, 97, 114, 116]))]
 for _v3e592be3242e in payload[''.join((chr(n) for n in [99, 111, 109, 109, 97, 110, 100, 115]))]:
  _v5a626e8a3745 = _vdbbedb3807b3[_v3e592be3242e](_v5a626e8a3745)
 return _identity_1(_v5a626e8a3745)
def _identity_1(value):
 return value
