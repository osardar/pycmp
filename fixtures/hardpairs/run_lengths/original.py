def run(p):
    result = []
    for item in p:
        if result and result[-1][0] == item:
            result[-1][1] += 1
        else:
            result.append([item, 1])
    return result
