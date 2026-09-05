"""Python 3.4: deterministic cleanup through a context manager."""
class Transaction(object):
    def __init__(self): self.events = []
    def __enter__(self):
        self.events.append("open")
        return self
    def __exit__(self, kind, value, trace):
        self.events.append("rollback" if kind else "commit")
        return False

def record():
    with Transaction() as transaction:
        transaction.events.append("write")
    return transaction.events
