def _v1e617445e110(_v694fef7c4a10):
 return _v694fef7c4a10 + 3
def _v3e01d0f7737e(_v694fef7c4a10):
 return _v694fef7c4a10 - 2
def run(payload):
 _vc068b0fd6a91 = {'up': _v1e617445e110, 'down': _v3e01d0f7737e}
 _v0a15a1ce0fdb = payload['start']
 for _vd1a98505c7cf in payload['commands']:
  _v0a15a1ce0fdb = _vc068b0fd6a91[_vd1a98505c7cf](_v0a15a1ce0fdb)
 return _v0a15a1ce0fdb
