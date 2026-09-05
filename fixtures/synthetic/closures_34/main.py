"""Python 3.4: decorators, closures, and nonlocal state."""
def counted(function):
    calls = [0]
    def wrapper(*args, **kwargs):
        calls[0] += 1
        return function(*args, **kwargs), calls[0]
    return wrapper

@counted
def double(value): return value * 2
