import json
def run(payload):
 _v26ac52cb1be7 = json.dumps(payload, sort_keys=True).encode('utf-8')
 _v618ccbe628be = json.loads(_v26ac52cb1be7.decode('utf-8'))
 return {'keys': sorted(_v618ccbe628be), 'values': [_v618ccbe628be[_v68ff685777bd] for _v68ff685777bd in sorted(_v618ccbe628be)]}
