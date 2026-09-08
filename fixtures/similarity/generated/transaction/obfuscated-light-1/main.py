class _v51a534a006b8:
 def __init__(self, _v135daac92864):
  self.values = _v135daac92864
  self.saved = list(_v135daac92864)
 def __enter__(self):
  return self.values
 def __exit__(self, _va965cc693bcf, _ve084cd3b4a03, _vd5988560963f):
  if _va965cc693bcf is not None:
   self.values[:] = self.saved
  return _va965cc693bcf is ValueError
def run(payload):
 _v135daac92864 = list(payload['values'])
 with _v51a534a006b8(_v135daac92864) as _vd1879bb0f2ef:
  _vd1879bb0f2ef.append(9)
  if payload['rollback']:
   raise ValueError('rollback')
 return _v135daac92864
