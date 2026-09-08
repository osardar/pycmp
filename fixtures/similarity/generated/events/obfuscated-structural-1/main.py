def _vf590ceb0bc85(_v135daac92864, _v0211e9c634d0):
 for _v89a28dc40530 in range(0, len(_v135daac92864), _v0211e9c634d0):
  yield _v135daac92864[_v89a28dc40530:_v89a28dc40530 + _v0211e9c634d0]
def run(payload):
 _v4a0880d92179 = (_v8711e39e3d7d for _v8711e39e3d7d in payload[''.join((chr(n) for n in [118, 97, 108, 117, 101, 115]))] if _v8711e39e3d7d >= 0)
 return _identity_1([sum(_v12c419604f66) for _v12c419604f66 in _vf590ceb0bc85(list(_v4a0880d92179), 2)])
def _identity_1(value):
 return value
