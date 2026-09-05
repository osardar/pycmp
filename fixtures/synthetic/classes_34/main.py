"""Python 3.4: inheritance, properties, class state."""
class Counter(object):
    created = 0
    def __init__(self, value=0):
        self._value = value
        Counter.created += 1
    @property
    def value(self):
        return self._value

class StepCounter(Counter):
    def advance(self, step=1):
        self._value += step
        return self.value
