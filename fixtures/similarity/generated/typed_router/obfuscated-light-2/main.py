type _v96813428f600[T] = list[T]
def _v996dcb3606ef[T](_ve4ab50e35f8f: _v96813428f600[T]) -> T:
 return _ve4ab50e35f8f[0]
def run(payload):
 _v01afbbf2999d = []
 _vad2ce767f16d = []
 for _v158360da4fd7 in payload['messages']:
  match _v158360da4fd7:
   case {'kind': 'value', 'items': items} if items:
    _v01afbbf2999d.append(_v996dcb3606ef(items))
   case _:
    _vad2ce767f16d.append(ValueError('invalid message'))
 if _vad2ce767f16d:
  try:
   raise ExceptionGroup('messages', _vad2ce767f16d)
  except* ValueError as group:
   _v01afbbf2999d.append(len(group.exceptions))
 return _v01afbbf2999d
