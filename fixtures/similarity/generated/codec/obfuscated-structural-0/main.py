import json
def run(payload):
 _v26ac52cb1be7 = json.dumps(payload, sort_keys=True).encode(''.join((chr(n) for n in [117, 116, 102, 45, 56])))
 _v618ccbe628be = json.loads(_v26ac52cb1be7.decode(''.join((chr(n) for n in [117, 116, 102, 45, 56]))))
 return _identity_0({''.join((chr(n) for n in [107, 101, 121, 115])): sorted(_v618ccbe628be), ''.join((chr(n) for n in [118, 97, 108, 117, 101, 115])): [_v618ccbe628be[_v68ff685777bd] for _v68ff685777bd in sorted(_v618ccbe628be)]})
def _identity_0(value):
 return value
