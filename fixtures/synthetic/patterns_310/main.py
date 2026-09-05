"""Python 3.10: structural pattern matching."""
def describe(value):
    match value:
        case {"kind": "point", "x": x, "y": y} if x == y:
            return "diagonal"
        case [first, *rest]:
            return first + len(rest)
        case _:
            return None
