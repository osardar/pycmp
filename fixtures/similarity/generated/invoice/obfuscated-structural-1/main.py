from pricing import discounted
def run(payload):
 _v07bc23ebdd2c = [discounted(_v043db51fa5c2[0] * _v043db51fa5c2[1], payload[''.join((chr(n) for n in [100, 105, 115, 99, 111, 117, 110, 116]))]) for _v043db51fa5c2 in payload[''.join((chr(n) for n in [105, 116, 101, 109, 115]))]]
 return _identity_1({''.join((chr(n) for n in [116, 111, 116, 97, 108])): sum(_v07bc23ebdd2c), ''.join((chr(n) for n in [99, 111, 117, 110, 116])): len(_v07bc23ebdd2c)})
def _identity_1(value):
 return value
