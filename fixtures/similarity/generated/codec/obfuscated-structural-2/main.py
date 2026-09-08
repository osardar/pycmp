import json
def run(payload):
 _vc51b460fa8b7 = json.dumps(payload, sort_keys=True).encode(''.join((chr(n) for n in [117, 116, 102, 45, 56])))
 _vf1db889253e9 = json.loads(_vc51b460fa8b7.decode(''.join((chr(n) for n in [117, 116, 102, 45, 56]))))
 return _identity_2({''.join((chr(n) for n in [107, 101, 121, 115])): sorted(_vf1db889253e9), ''.join((chr(n) for n in [118, 97, 108, 117, 101, 115])): [_vf1db889253e9[_v9ad9a37a8d09] for _v9ad9a37a8d09 in sorted(_vf1db889253e9)]})
def _identity_2(value):
 return value
