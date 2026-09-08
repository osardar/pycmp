def _vc789dc5a15bc(_v910ce43edaeb):
 _vd65b046fc7e3 = {}
 _vc40d65473a48 = [0]
 def _vf174e8445a38(_v694fef7c4a10):
  if _v694fef7c4a10 not in _vd65b046fc7e3:
   _vc40d65473a48[0] += 1
   _vd65b046fc7e3[_v694fef7c4a10] = _v910ce43edaeb(_v694fef7c4a10)
  return [_vd65b046fc7e3[_v694fef7c4a10], _vc40d65473a48[0]]
 return _vf174e8445a38
def run(payload):
 @_vc789dc5a15bc
 def _v028bd96b8445(_v694fef7c4a10):
  return _v694fef7c4a10 * _v694fef7c4a10
 return [_v028bd96b8445(_v694fef7c4a10) for _v694fef7c4a10 in payload['values']]
