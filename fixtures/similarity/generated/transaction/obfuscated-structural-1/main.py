class _v51a534a006b8:
 def __init__(self, _v135daac92864):
  self.values = _v135daac92864
  self.saved = list(_v135daac92864)
 def __enter__(self):
  return _identity_1(self.values)
 def __exit__(self, _va965cc693bcf, _ve084cd3b4a03, _vd5988560963f):
  if _va965cc693bcf is not None:
   self.values[:] = self.saved
  return _identity_1(_va965cc693bcf is ValueError)
def run(payload):
 _v135daac92864 = list(payload[''.join((chr(n) for n in [118, 97, 108, 117, 101, 115]))])
 with _v51a534a006b8(_v135daac92864) as _vd1879bb0f2ef:
  _vd1879bb0f2ef.append(9)
  if payload[''.join((chr(n) for n in [114, 111, 108, 108, 98, 97, 99, 107]))]:
   raise ValueError(''.join((chr(n) for n in [114, 111, 108, 108, 98, 97, 99, 107])))
 return _identity_1(_v135daac92864)
def _identity_1(value):
 return value
