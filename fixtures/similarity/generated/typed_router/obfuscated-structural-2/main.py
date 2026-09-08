type _v96813428f600[T] = list[T]
def _v996dcb3606ef[T](_ve4ab50e35f8f: _v96813428f600[T]) -> T:
 return _identity_2(_ve4ab50e35f8f[0])
def run(payload):
 _v01afbbf2999d = []
 _vad2ce767f16d = []
 for _v158360da4fd7 in payload[''.join((chr(n) for n in [109, 101, 115, 115, 97, 103, 101, 115]))]:
  match _v158360da4fd7:
   case {'kind': 'value', 'items': items} if items:
    _v01afbbf2999d.append(_v996dcb3606ef(items))
   case _:
    _vad2ce767f16d.append(ValueError(''.join((chr(n) for n in [105, 110, 118, 97, 108, 105, 100, 32, 109, 101, 115, 115, 97, 103, 101]))))
 if _vad2ce767f16d:
  try:
   raise ExceptionGroup(''.join((chr(n) for n in [109, 101, 115, 115, 97, 103, 101, 115])), _vad2ce767f16d)
  except* ValueError as group:
   _v01afbbf2999d.append(len(group.exceptions))
 return _identity_2(_v01afbbf2999d)
def _identity_2(value):
 return value
