"""Python 3.6: annotations, keyword-only arguments, f-strings."""
def label(name: str, *, count: int = 1) -> str:
    return f"{name}:{count}"

def annotate(values):
    result: list = [label(value, count=index) for index, value in enumerate(values)]
    return result
