def memoized(function):
    cache = {}
    calls = [0]
    def wrapped(value):
        if value not in cache:
            calls[0] += 1
            cache[value] = function(value)
        return [cache[value], calls[0]]
    return wrapped

def run(payload):
    @memoized
    def square(value):
        return value * value
    return [square(value) for value in payload["values"]]
