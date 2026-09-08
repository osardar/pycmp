def _vf590ceb0bc85(_v135daac92864, _v0211e9c634d0):
 for _v89a28dc40530 in range(0, len(_v135daac92864), _v0211e9c634d0):
  yield _v135daac92864[_v89a28dc40530:_v89a28dc40530 + _v0211e9c634d0]
def run(payload):
 _v4a0880d92179 = (_v8711e39e3d7d for _v8711e39e3d7d in payload['values'] if _v8711e39e3d7d >= 0)
 return [sum(_v12c419604f66) for _v12c419604f66 in _vf590ceb0bc85(list(_v4a0880d92179), 2)]
