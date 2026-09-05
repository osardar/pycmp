"""Cross-lane contrastive training primitives."""
from __future__ import annotations

from dataclasses import dataclass

import torch

from .semantic import ProgramGraph
from .shared_model import SharedGraphEncoder, contrastive_loss


@dataclass(frozen=True)
class TrainingView:
    graph: ProgramGraph
    artifact_id: str
    view_kind: str  # source, bytecode, decompiled, damaged, transformed


def positive_pairs(views: list[TrainingView]) -> list[tuple[int, int]]:
    """Pair different views of one artifact; same-lane duplicates are excluded."""
    pairs: list[tuple[int, int]] = []
    for left, a in enumerate(views):
        for right, b in enumerate(views[left + 1:], start=left + 1):
            if a.artifact_id == b.artifact_id and a.view_kind != b.view_kind:
                pairs.append((left, right))
    return pairs


def train_step(model: SharedGraphEncoder, optimizer: torch.optim.Optimizer,
               views: list[TrainingView]) -> float:
    pairs = positive_pairs(views)
    if not pairs:
        raise ValueError("batch needs two distinct views of at least one artifact")
    model.train()
    optimizer.zero_grad()
    vectors = model(view.graph for view in views)
    loss = contrastive_loss(vectors, pairs)
    loss.backward()
    optimizer.step()
    return float(loss.detach())
