"""Python 3.4: custom iteration and comprehensions."""
class Squares(object):
    def __init__(self, count): self.count = count
    def __iter__(self):
        for value in range(self.count):
            yield value * value

def odd_squares(count):
    return [value for value in Squares(count) if value % 2]
