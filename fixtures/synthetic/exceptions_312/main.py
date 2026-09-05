"""Python 3.12: type parameters, aliases, and exception groups."""
type Box[T] = list[T]

def first[T](values: Box[T]) -> T:
    return values[0]

def handle(group):
    count = 0
    try:
        raise group
    except* ValueError as errors:
        count = len(errors.exceptions)
    return count
