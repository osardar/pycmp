class Stock:
    def __init__(self, amount):
        self.amount = amount

    @property
    def remaining(self):
        return self.amount

    def remove(self, count):
        if count > self.amount:
            raise ValueError("stock exhausted")
        self.amount -= count

class ReservedStock(Stock):
    def available(self):
        return max(0, self.remaining - 2)

def run(payload):
    stock = ReservedStock(payload["initial"])
    for count in payload["orders"]:
        stock.remove(count)
    return [stock.remaining, stock.available()]
