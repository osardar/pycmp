type _vaf17d9405931[T] = list[T]
def _v8ad494e0ab1e[T](_v46070de93fe0: _vaf17d9405931[T]) -> T:
 return _v46070de93fe0[0]
def run(payload):
 _vc8c8f3029259 = []
 _v0303aaf89dc6 = []
 for _v66f7feac13d0 in payload['messages']:
  match _v66f7feac13d0:
   case {'kind': 'value', 'items': items} if items:
    _vc8c8f3029259.append(_v8ad494e0ab1e(items))
   case _:
    _v0303aaf89dc6.append(ValueError('invalid message'))
 if _v0303aaf89dc6:
  try:
   raise ExceptionGroup('messages', _v0303aaf89dc6)
  except* ValueError as group:
   _vc8c8f3029259.append(len(group.exceptions))
 return _vc8c8f3029259
