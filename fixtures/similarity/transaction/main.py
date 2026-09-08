class Transaction:
    def __init__(self, values):
        self.values = values
        self.saved = list(values)

    def __enter__(self):
        return self.values

    def __exit__(self, kind, error, trace):
        if kind is not None:
            self.values[:] = self.saved
        return kind is ValueError

def run(payload):
    values = list(payload["values"])
    with Transaction(values) as target:
        target.append(9)
        if payload["rollback"]:
            raise ValueError("rollback")
    return values
