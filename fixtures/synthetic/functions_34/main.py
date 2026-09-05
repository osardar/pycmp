"""Python 3.4: calls, defaults, variadics, recursion."""
def total(values, start=0, *extra, **options):
    if not values:
        return start + sum(extra) + options.get("bonus", 0)
    return total(values[1:], start + values[0], *extra, **options)
