def _v07de580ab267(_v5c23804d9f99):
 _v7313c0d89803 = {}
 _vc0f1dd957ace = [0]
 def _v59d3e29052c4(_vb54a57e5caef):
  if _vb54a57e5caef not in _v7313c0d89803:
   _vc0f1dd957ace[0] += 1
   _v7313c0d89803[_vb54a57e5caef] = _v5c23804d9f99(_vb54a57e5caef)
  return [_v7313c0d89803[_vb54a57e5caef], _vc0f1dd957ace[0]]
 return _v59d3e29052c4
def run(payload):
 @_v07de580ab267
 def _ved882e012ada(_vb54a57e5caef):
  return _vb54a57e5caef * _vb54a57e5caef
 return [_ved882e012ada(_vb54a57e5caef) for _vb54a57e5caef in payload['values']]
