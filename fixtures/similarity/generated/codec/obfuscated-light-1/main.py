import json
def run(payload):
 _ve5b643f9838b = json.dumps(payload, sort_keys=True).encode('utf-8')
 _v4dce17b6ab49 = json.loads(_ve5b643f9838b.decode('utf-8'))
 return {'keys': sorted(_v4dce17b6ab49), 'values': [_v4dce17b6ab49[_v06706879631b] for _v06706879631b in sorted(_v4dce17b6ab49)]}
