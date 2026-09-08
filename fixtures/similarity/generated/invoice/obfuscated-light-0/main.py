from pricing import discounted
def run(payload):
 _vfdf7fd088a02 = [discounted(_v6865cc720b11[0] * _v6865cc720b11[1], payload['discount']) for _v6865cc720b11 in payload['items']]
 return {'total': sum(_vfdf7fd088a02), 'count': len(_vfdf7fd088a02)}
