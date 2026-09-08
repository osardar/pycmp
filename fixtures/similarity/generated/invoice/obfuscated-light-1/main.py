from pricing import discounted
def run(payload):
 _v07bc23ebdd2c = [discounted(_v043db51fa5c2[0] * _v043db51fa5c2[1], payload['discount']) for _v043db51fa5c2 in payload['items']]
 return {'total': sum(_v07bc23ebdd2c), 'count': len(_v07bc23ebdd2c)}
