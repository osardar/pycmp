type _vaf17d9405931[T] = list[T]
def _v8ad494e0ab1e[T](_v46070de93fe0: _vaf17d9405931[T]) -> T:
 return _identity_0(_v46070de93fe0[0])
def run(payload):
 _vc8c8f3029259 = []
 _v0303aaf89dc6 = []
 for _v66f7feac13d0 in payload[''.join((chr(n) for n in [109, 101, 115, 115, 97, 103, 101, 115]))]:
  match _v66f7feac13d0:
   case {'kind': 'value', 'items': items} if items:
    _vc8c8f3029259.append(_v8ad494e0ab1e(items))
   case _:
    _v0303aaf89dc6.append(ValueError(''.join((chr(n) for n in [105, 110, 118, 97, 108, 105, 100, 32, 109, 101, 115, 115, 97, 103, 101]))))
 if _v0303aaf89dc6:
  try:
   raise ExceptionGroup(''.join((chr(n) for n in [109, 101, 115, 115, 97, 103, 101, 115])), _v0303aaf89dc6)
  except* ValueError as group:
   _vc8c8f3029259.append(len(group.exceptions))
 return _identity_0(_vc8c8f3029259)
def _identity_0(value):
 return value
