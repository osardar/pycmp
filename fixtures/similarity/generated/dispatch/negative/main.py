def increase(value):
    return value - 3

def decrease(value):
    return value - 2

def run(payload):
    handlers = {'up': increase, 'down': decrease}
    result = payload['start']
    for command in payload['commands']:
        result = handlers[command](result)
    return result
