import json

def _original_run(payload):
    encoded = json.dumps(payload, sort_keys=True).encode('utf-8')
    decoded = json.loads(encoded.decode('utf-8'))
    return {'keys': sorted(decoded), 'values': [decoded[key] for key in sorted(decoded)]}

def run(payload):
    return [_original_run(payload), 'changed']
