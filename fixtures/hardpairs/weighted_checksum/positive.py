def run(p):
    return sum((i + 1) * x for i, x in enumerate(p)) % 17
