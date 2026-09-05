"""The versioned graph contract shared by every ingestion lane."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


SCHEMA_VERSION = 1


@dataclass(frozen=True)
class GraphNode:
    id: str
    kind: str
    attributes: dict[str, Any] = field(default_factory=dict)
    available: tuple[str, ...] = ()


@dataclass(frozen=True)
class GraphEdge:
    source: str
    target: str
    kind: str
    available: tuple[str, ...] = ()


@dataclass
class ProgramGraph:
    """A serializable semantic graph for one comparable program unit.

    ``available`` records facts observed by a lane. Missing facts are therefore
    not confused with a known false/empty fact by downstream models.
    """

    unit_id: str
    unit_kind: str
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    metadata: dict[str, Any] = field(default_factory=dict)
    schema_version: int = SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "unit_id": self.unit_id,
            "unit_kind": self.unit_kind,
            "nodes": [asdict(node) for node in self.nodes],
            "edges": [asdict(edge) for edge in self.edges],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ProgramGraph":
        if value.get("schema_version") != SCHEMA_VERSION:
            raise ValueError(f"unsupported graph schema: {value.get('schema_version')}")
        return cls(
            unit_id=value["unit_id"],
            unit_kind=value["unit_kind"],
            nodes=[GraphNode(**node) for node in value["nodes"]],
            edges=[GraphEdge(**edge) for edge in value["edges"]],
            metadata=value.get("metadata", {}),
            schema_version=value["schema_version"],
        )
