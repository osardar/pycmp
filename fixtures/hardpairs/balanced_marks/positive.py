def run(p):
    pending = []
    for mark in p:
        if mark == '(':
            pending.append(mark)
        elif pending:
            pending.pop()
        else:
            return False
    return not pending
