def run(p):
    from itertools import groupby
    return [[key, len(list(group))] for key, group in groupby(p)]
