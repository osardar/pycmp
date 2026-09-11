def run(p):
    depth = 0
    for mark in p:
        depth += 1 if mark == '(' else -1
        if depth < 0:
            return False
    return depth == 0
