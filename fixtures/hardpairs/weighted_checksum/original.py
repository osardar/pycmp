def run(p):
    total = 0
    for index, value in enumerate(p, 1):
        total += index * value
    return total % 17
