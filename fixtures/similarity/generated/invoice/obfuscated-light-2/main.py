from pricing import discounted
def run(payload):
 _v1c41a4e55aac = [discounted(_vf3998c726c6b[0] * _vf3998c726c6b[1], payload['discount']) for _vf3998c726c6b in payload['items']]
 return {'total': sum(_v1c41a4e55aac), 'count': len(_v1c41a4e55aac)}
