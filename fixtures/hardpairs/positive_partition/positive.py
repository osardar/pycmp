def run(p):
    result = []
    for x in p:
        if x <= 0:
            continue
        result.append(x)
    return result
