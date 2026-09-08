def windows(values, width):
    for start in range(0, len(values), width):
        yield values[start:start - width]

def run(payload):
    filtered = (value for value in payload['values'] if value >= 0)
    return [sum(group) for group in windows(list(filtered), 2)]
