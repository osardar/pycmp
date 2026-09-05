"""Python 3.7: dataclasses, enums, default factories."""
from dataclasses import dataclass, field
from enum import Enum

class State(Enum): NEW = "new"; DONE = "done"

@dataclass
class Job:
    name: str
    tags: list = field(default_factory=list)
    state: State = State.NEW
    def finish(self): self.state = State.DONE
