def _vf3f2ee016c5a(_v93f0d7a0b00c, _v26a996347d3d, _v408b4939f675, _v5cec851903a6):
 if _v93f0d7a0b00c in _v408b4939f675:
  return
 _v408b4939f675.add(_v93f0d7a0b00c)
 for _vcff534212501 in _v26a996347d3d.get(_v93f0d7a0b00c, []):
  _vf3f2ee016c5a(_vcff534212501, _v26a996347d3d, _v408b4939f675, _v5cec851903a6)
 _v5cec851903a6.append(_v93f0d7a0b00c)
def run(payload):
 _v5cec851903a6 = []
 _vf3f2ee016c5a(payload[''.join((chr(n) for n in [114, 111, 111, 116]))], payload[''.join((chr(n) for n in [103, 114, 97, 112, 104]))], set(), _v5cec851903a6)
 return _identity_1(_v5cec851903a6)
def _identity_1(value):
 return value
