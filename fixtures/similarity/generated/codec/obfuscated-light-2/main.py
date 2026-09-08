import json
def run(payload):
 _vc51b460fa8b7 = json.dumps(payload, sort_keys=True).encode('utf-8')
 _vf1db889253e9 = json.loads(_vc51b460fa8b7.decode('utf-8'))
 return {'keys': sorted(_vf1db889253e9), 'values': [_vf1db889253e9[_v9ad9a37a8d09] for _v9ad9a37a8d09 in sorted(_vf1db889253e9)]}
