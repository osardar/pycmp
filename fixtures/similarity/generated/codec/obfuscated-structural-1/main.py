import json
def run(payload):
 _ve5b643f9838b = json.dumps(payload, sort_keys=True).encode(''.join((chr(n) for n in [117, 116, 102, 45, 56])))
 _v4dce17b6ab49 = json.loads(_ve5b643f9838b.decode(''.join((chr(n) for n in [117, 116, 102, 45, 56]))))
 return _identity_1({''.join((chr(n) for n in [107, 101, 121, 115])): sorted(_v4dce17b6ab49), ''.join((chr(n) for n in [118, 97, 108, 117, 101, 115])): [_v4dce17b6ab49[_v06706879631b] for _v06706879631b in sorted(_v4dce17b6ab49)]})
def _identity_1(value):
 return value
