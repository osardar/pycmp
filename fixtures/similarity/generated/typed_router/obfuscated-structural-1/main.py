type _vf15a69ac8ccd[T] = list[T]
def _va59ca83dd51b[T](_v135daac92864: _vf15a69ac8ccd[T]) -> T:
 return _identity_1(_v135daac92864[0])
def run(payload):
 _v5cec851903a6 = []
 _v3b39ede47da7 = []
 for _vfd1693231eb8 in payload[''.join((chr(n) for n in [109, 101, 115, 115, 97, 103, 101, 115]))]:
  match _vfd1693231eb8:
   case {'kind': 'value', 'items': items} if items:
    _v5cec851903a6.append(_va59ca83dd51b(items))
   case _:
    _v3b39ede47da7.append(ValueError(''.join((chr(n) for n in [105, 110, 118, 97, 108, 105, 100, 32, 109, 101, 115, 115, 97, 103, 101]))))
 if _v3b39ede47da7:
  try:
   raise ExceptionGroup(''.join((chr(n) for n in [109, 101, 115, 115, 97, 103, 101, 115])), _v3b39ede47da7)
  except* ValueError as group:
   _v5cec851903a6.append(len(group.exceptions))
 return _identity_1(_v5cec851903a6)
def _identity_1(value):
 return value
