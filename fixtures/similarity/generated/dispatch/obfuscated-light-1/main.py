def _va7cd44d578a7(_v8711e39e3d7d):
 return _v8711e39e3d7d + 3
def _v124fb42e5ef8(_v8711e39e3d7d):
 return _v8711e39e3d7d - 2
def run(payload):
 _vdbbedb3807b3 = {'up': _va7cd44d578a7, 'down': _v124fb42e5ef8}
 _v5a626e8a3745 = payload['start']
 for _v3e592be3242e in payload['commands']:
  _v5a626e8a3745 = _vdbbedb3807b3[_v3e592be3242e](_v5a626e8a3745)
 return _v5a626e8a3745
