def run(p):
    try:
        return p[0] // p[1]
    except ZeroDivisionError:
        return None
