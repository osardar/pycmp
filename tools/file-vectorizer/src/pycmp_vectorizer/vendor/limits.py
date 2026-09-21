"""Deployment-only graph admission limits; never truncate graphs."""
_counts = {"nodes": 0, "edges": 0}
_limits = {"nodes": 10000, "edges": 100000}


def reset(nodes, edges):
    _counts.update(nodes=0, edges=0)
    _limits.update(nodes=nodes, edges=edges)


class LimitedList(list):
    def __init__(self, kind):
        super().__init__()
        self.kind = kind

    def append(self, value):
        _counts[self.kind] += 1
        if _counts[self.kind] > _limits[self.kind]:
            raise ValueError("node_limit" if self.kind == "nodes" else "edge_limit")
        super().append(value)
