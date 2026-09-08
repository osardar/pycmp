def _v1e617445e110(_v694fef7c4a10):
 return _identity_2(_v694fef7c4a10 + 3)
def _v3e01d0f7737e(_v694fef7c4a10):
 return _identity_2(_v694fef7c4a10 - 2)
def run(payload):
 _vc068b0fd6a91 = {''.join((chr(n) for n in [117, 112])): _v1e617445e110, ''.join((chr(n) for n in [100, 111, 119, 110])): _v3e01d0f7737e}
 _v0a15a1ce0fdb = payload[''.join((chr(n) for n in [115, 116, 97, 114, 116]))]
 for _vd1a98505c7cf in payload[''.join((chr(n) for n in [99, 111, 109, 109, 97, 110, 100, 115]))]:
  _v0a15a1ce0fdb = _vc068b0fd6a91[_vd1a98505c7cf](_v0a15a1ce0fdb)
 return _identity_2(_v0a15a1ce0fdb)
def _identity_2(value):
 return value
