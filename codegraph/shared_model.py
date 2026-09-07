"""One masked relational encoder for every semantic-program-graph lane."""
from __future__ import annotations

import hashlib
from collections.abc import Iterable

import torch
from torch import nn

from .semantic import ProgramGraph


FEATURE_KEYS = (
    "ast_type", "semantic_kind", "constant_category", "name_context",
    "attribute_hash", "opcode", "operand_category", "recovery_type",
)


def _bucket(value: str, size: int) -> int:
    return int.from_bytes(hashlib.blake2b(value.encode(), digest_size=8).digest(), "big") % size


def graph_tensors(graph: ProgramGraph, *, node_buckets: int, relation_buckets: int) -> dict[str, torch.Tensor]:
    positions = {node.id: i for i, node in enumerate(graph.nodes)}
    graph.validate()
    feature_rows: list[list[int]] = []
    feature_masks: list[list[float]] = []
    for node in graph.nodes:
        tokens = [f"kind={node.kind}"]
        tokens.extend(f"{key}={node.attributes[key]}" for key in FEATURE_KEYS if key in node.attributes)
        feature_rows.append([_bucket(token, node_buckets) for token in tokens])
    width = max(len(row) for row in feature_rows)
    for row in feature_rows:
        feature_masks.append([1.0] * len(row) + [0.0] * (width - len(row)))
        row.extend([0] * (width - len(row)))
    feature_ids = torch.tensor(feature_rows, dtype=torch.long)
    feature_mask = torch.tensor(feature_masks, dtype=torch.float32)
    node_types = feature_ids[:, 0]
    # At least one availability fact is known for all nodes. The ratio gives the
    # model a direct, portable missing-information signal without lane IDs.
    availability = torch.tensor(
        [[min(len(node.available), 8) / 8.0, 1.0 if node.attributes else 0.0] for node in graph.nodes],
        dtype=torch.float32,
    )
    kept = [edge for edge in graph.edges if edge.source in positions and edge.target in positions]
    edge_index = torch.tensor([[positions[e.source], positions[e.target]] for e in kept], dtype=torch.long)
    if not kept:
        edge_index = torch.empty((0, 2), dtype=torch.long)
    edge_types = torch.tensor([
        _bucket(f"{edge.kind}|position={edge.attributes.get('position', '*')}", relation_buckets)
        for edge in kept
    ], dtype=torch.long)
    return {"node_types": node_types, "availability": availability,
            "feature_ids": feature_ids, "feature_mask": feature_mask,
            "edge_index": edge_index, "edge_types": edge_types}


class RelationalLayer(nn.Module):
    def __init__(self, dimension: int) -> None:
        super().__init__()
        self.update = nn.Sequential(nn.Linear(dimension * 2, dimension), nn.ReLU(), nn.LayerNorm(dimension))

    def forward(self, values: torch.Tensor, edge_index: torch.Tensor, relation: torch.Tensor) -> torch.Tensor:
        if edge_index.numel() == 0:
            return self.update(torch.cat((values, torch.zeros_like(values)), dim=-1))
        source, target = edge_index.unbind(dim=1)
        messages = values[source] + relation
        aggregate = torch.zeros_like(values)
        aggregate.index_add_(0, target, messages)
        degree = torch.zeros(values.shape[0], 1, device=values.device)
        degree.index_add_(0, target, torch.ones((target.shape[0], 1), device=values.device))
        return self.update(torch.cat((values, aggregate / degree.clamp_min(1)), dim=-1))


class SharedGraphEncoder(nn.Module):
    """A lane-agnostic relational GNN yielding L2-normalized graph vectors."""

    def __init__(self, dimension: int = 256, layers: int = 4,
                 node_buckets: int = 2048, relation_buckets: int = 512) -> None:
        super().__init__()
        self.dimension = dimension
        self.node_buckets = node_buckets
        self.relation_buckets = relation_buckets
        self.node_embedding = nn.Embedding(node_buckets, dimension)
        self.relation_embedding = nn.Embedding(relation_buckets, dimension)
        self.layers = nn.ModuleList(RelationalLayer(dimension) for _ in range(layers))
        self.project = nn.Linear(dimension, dimension)

    def encode_graph(self, graph: ProgramGraph) -> torch.Tensor:
        tensors = graph_tensors(graph, node_buckets=self.node_buckets,
                                relation_buckets=self.relation_buckets)
        device = next(self.parameters()).device
        feature_ids = tensors["feature_ids"].to(device)
        feature_mask = tensors["feature_mask"].to(device)
        features = self.node_embedding(feature_ids)
        # The first token is the lane-independent semantic core. Optional
        # evidence refines it at a bounded weight and its absence is not encoded
        # as a lane-identifying feature.
        values = features[:, 0]
        optional_mask = feature_mask[:, 1:]
        if optional_mask.shape[1]:
            optional = (features[:, 1:] * optional_mask[..., None]).sum(dim=1)
            optional = optional / optional_mask.sum(dim=1, keepdim=True).clamp_min(1)
            values = values + 0.25 * optional
        edge_index, edge_types = tensors["edge_index"].to(device), tensors["edge_types"].to(device)
        for layer in self.layers:
            values = layer(values, edge_index, self.relation_embedding(edge_types))
        return torch.nn.functional.normalize(self.project(values.mean(dim=0)), dim=0)

    def forward(self, graphs: Iterable[ProgramGraph]) -> torch.Tensor:
        return torch.stack([self.encode_graph(graph) for graph in graphs])


class ProjectEmbeddingPool(nn.Module):
    """Learned function-to-project pooling in the same embedding space."""

    def __init__(self, dimension: int = 256) -> None:
        super().__init__()
        self.attention = nn.Sequential(nn.Linear(dimension, dimension), nn.Tanh(), nn.Linear(dimension, 1))

    def forward(self, function_embeddings: torch.Tensor) -> torch.Tensor:
        if function_embeddings.ndim != 2 or function_embeddings.shape[0] == 0:
            raise ValueError("expected one or more function embeddings")
        weights = torch.softmax(self.attention(function_embeddings).squeeze(-1), dim=0)
        return torch.nn.functional.normalize((weights[:, None] * function_embeddings).sum(dim=0), dim=0)


def hybrid_project_similarity(left_project: torch.Tensor, right_project: torch.Tensor,
                              left_functions: torch.Tensor, right_functions: torch.Tensor,
                              top_k: int = 5, project_weight: float = 0.5) -> torch.Tensor:
    """Blend architectural similarity with explainable best-function matches."""
    project_score = torch.nn.functional.cosine_similarity(left_project, right_project, dim=0)
    matches = torch.nn.functional.normalize(left_functions, dim=-1) @ torch.nn.functional.normalize(right_functions, dim=-1).T
    k = min(top_k, matches.numel())
    function_score = matches.flatten().topk(k).values.mean()
    return project_weight * project_score + (1.0 - project_weight) * function_score


def contrastive_loss(embeddings: torch.Tensor, positive_pairs: list[tuple[int, int]], temperature: float = 0.07) -> torch.Tensor:
    """Multi-positive supervised contrastive loss with self excluded."""
    if not positive_pairs:
        raise ValueError("at least one positive pair is required")
    embeddings = torch.nn.functional.normalize(embeddings, dim=-1)
    if embeddings.shape[0] < 2:
        raise ValueError("at least two embeddings are required")
    logits = embeddings @ embeddings.T / temperature
    logits.fill_diagonal_(float("-inf"))
    positives: dict[int, set[int]] = {}
    for left, right in positive_pairs:
        if left == right or min(left, right) < 0 or max(left, right) >= embeddings.shape[0]:
            raise ValueError("positive pair indices must identify distinct embeddings")
        positives.setdefault(left, set()).add(right)
        positives.setdefault(right, set()).add(left)
    losses = []
    for anchor, matches in positives.items():
        numerator = torch.logsumexp(logits[anchor, list(matches)], dim=0)
        denominator = torch.logsumexp(logits[anchor], dim=0)
        losses.append(-(numerator - denominator))
    return torch.stack(losses).mean()
