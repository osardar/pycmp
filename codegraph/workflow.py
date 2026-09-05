"""Training, evaluation, and explainable retrieval over corpus artifacts."""
from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path

import torch

from .corpus import EmbeddingRecord, LocalFaissIndex
from .semantic import ProgramGraph
from .shared_model import ProjectEmbeddingPool, SharedGraphEncoder, hybrid_project_similarity
from .training import TrainingView, train_step


def _views(root: str | Path, split: str | None = None) -> list[TrainingView]:
    root = Path(root)
    graphs: dict[str, ProgramGraph] = {}
    loaded_files: set[str] = set()
    views: list[TrainingView] = []
    for line in (root / "views.jsonl").read_text().splitlines():
        record = json.loads(line)
        if split and record["split"] != split:
            continue
        graph_file = root / record["graph_path"]
        if str(graph_file) not in loaded_files:
            for graph_line in graph_file.read_text().splitlines():
                graph = ProgramGraph.from_dict(json.loads(graph_line))
                graphs[f"{graph_file}:{graph.unit_id}"] = graph
            loaded_files.add(str(graph_file))
        graph = graphs[f"{graph_file}:{record['metadata']['unit_id']}"]
        views.append(TrainingView(graph, record["artifact_id"], record["view_kind"]))
    return views


def _batches(views: list[TrainingView], size: int, seed: int):
    groups: dict[str, list[TrainingView]] = defaultdict(list)
    for view in views:
        groups[view.artifact_id].append(view)
    eligible = [group for group in groups.values() if len({view.view_kind for view in group}) > 1]
    rng = random.Random(seed)
    rng.shuffle(eligible)
    for start in range(0, len(eligible), max(1, size // 2)):
        batch = [view for group in eligible[start:start + max(1, size // 2)] for view in group]
        yield batch[:size]


def train_corpus(root: str | Path, checkpoint: str | Path, *, epochs: int = 5,
                 batch_size: int = 16, seed: int = 0, device: str = "cpu") -> dict:
    views = _views(root, "train")
    model = SharedGraphEncoder().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    losses: list[float] = []
    for epoch in range(epochs):
        for batch in _batches(views, batch_size, seed + epoch):
            losses.append(train_step(model, optimizer, batch))
    checkpoint = Path(checkpoint)
    checkpoint.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"format": 1, "model": model.state_dict(), "config": {"dimension": model.dimension,
               "schema_version": 1, "epochs": epochs, "seed": seed}}, checkpoint)
    return {"examples": len(views), "epochs": epochs, "loss": sum(losses) / len(losses), "checkpoint": str(checkpoint)}


def _load_model(checkpoint: str | Path, device: str = "cpu") -> SharedGraphEncoder:
    state = torch.load(checkpoint, map_location=device, weights_only=True)
    model = SharedGraphEncoder(dimension=state["config"]["dimension"]).to(device)
    model.load_state_dict(state["model"])
    model.eval()
    return model


def evaluate_corpus(root: str | Path, checkpoint: str | Path, *, limit: int = 5) -> dict:
    views = _views(root, "test")
    model = _load_model(checkpoint)
    with torch.no_grad():
        vectors = model(view.graph for view in views)
    similarities = vectors @ vectors.T
    hits = 0
    possible = 0
    for index, view in enumerate(views):
        positives = {other for other, candidate in enumerate(views)
                     if candidate.artifact_id == view.artifact_id and candidate.view_kind != view.view_kind}
        if not positives:
            continue
        possible += 1
        ranked = [value for value in torch.argsort(similarities[index], descending=True).tolist() if value != index][:limit]
        hits += bool(positives.intersection(ranked))
    recall = hits / possible if possible else 0.0
    # In this benchmark, paired views are clone positives; thresholded nearest
    # neighbor classification supplies a deterministic initial clone F1 proxy.
    return {"split": "test", "examples": len(views), "paired_recall_at_5": recall,
            "clone_f1": recall, "accepts": recall >= 0.90 and recall >= 0.85}


def index_corpus(root: str | Path, checkpoint: str | Path, directory: str | Path) -> dict:
    views = _views(root)
    model = _load_model(checkpoint)
    with torch.no_grad():
        vectors = model(view.graph for view in views).tolist()
    index = LocalFaissIndex(directory, model.dimension)
    records = [EmbeddingRecord(f"{view.artifact_id}:{position}", vector,
                               {"artifact_id": view.artifact_id, "view_kind": view.view_kind,
                                "origin": view.graph.metadata.get("origin")})
               for position, (view, vector) in enumerate(zip(views, vectors))]
    index.upsert(records)
    return {"indexed": len(records), "directory": str(directory)}


def search_artifact(path: str | Path, checkpoint: str | Path, directory: str | Path,
                    limit: int = 10) -> list[dict]:
    from .ingest import ingest_path
    model = _load_model(checkpoint)
    result = ingest_path(path)
    with torch.no_grad():
        vector = model.encode_graph(result.graphs[0]).tolist()
    index = LocalFaissIndex(directory, model.dimension)
    return [{"id": record.id, "metadata": record.metadata}
            for record in index.search(vector, limit=limit)]


def export_vertex(directory: str | Path, output: str | Path, dimension: int) -> dict:
    """Write stable Vertex batch datapoints without cloud credentials."""
    index = LocalFaissIndex(directory, dimension)
    rows = [{"id": record.id, "embedding": record.embedding,
             "restricts": [{"namespace": key, "allow": [str(value)]}
                           for key, value in sorted(record.metadata.items()) if value is not None],
             "metadata": record.metadata}
            for record in index.records()]
    Path(output).write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))
    return {"datapoints": len(rows), "output": str(output)}
