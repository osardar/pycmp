"""Training, evaluation, and explainable retrieval over corpus artifacts."""
from __future__ import annotations

import json
import hashlib
import os
import random
import tempfile
from collections import defaultdict
from pathlib import Path

import torch

from .corpus import EmbeddingRecord, LocalFaissIndex
from .semantic import ProgramGraph, SCHEMA_VERSION
from .shared_model import FEATURE_KEYS, ProjectEmbeddingPool, SharedGraphEncoder, hybrid_project_similarity
from .training import TrainingView, train_step
from .curation import canonical_hash


def _view_entries(root: str | Path, split: str | None = None, *, semantic_only: bool = False) -> list[tuple[TrainingView, dict]]:
    root = Path(root)
    graphs: dict[str, ProgramGraph] = {}
    loaded_files: set[str] = set()
    views: list[tuple[TrainingView, dict]] = []
    records = [json.loads(line) for line in (root / "views.jsonl").read_text().splitlines()]
    needed: dict[str, set[str]] = defaultdict(set)
    for record in records:
        if split and record["split"] != split:
            continue
        if semantic_only and not record["metadata"].get("semantic_trainable", False):
            continue
        needed[record["graph_path"]].add(record["metadata"]["unit_id"])
    for record in records:
        if split and record["split"] != split:
            continue
        if semantic_only and not record["metadata"].get("semantic_trainable", False):
            continue
        graph_file = root / record["graph_path"]
        if str(graph_file) not in loaded_files:
            for graph_line in graph_file.read_text().splitlines():
                graph = ProgramGraph.from_dict(json.loads(graph_line))
                if graph.unit_id in needed[record["graph_path"]]:
                    graphs[f"{graph_file}:{graph.unit_id}"] = graph
            loaded_files.add(str(graph_file))
        graph = graphs[f"{graph_file}:{record['metadata']['unit_id']}"]
        views.append((TrainingView(graph, record["artifact_id"], record["view_kind"]), record["metadata"]))
    return views


def _views(root: str | Path, split: str | None = None, *, semantic_only: bool = False) -> list[TrainingView]:
    return [view for view, _ in _view_entries(root, split, semantic_only=semantic_only)]


def _batches(views: list[TrainingView], size: int, seed: int):
    if size < 2:
        raise ValueError("batch size must be at least two")
    groups: dict[str, list[TrainingView]] = defaultdict(list)
    for view in views:
        groups[view.artifact_id].append(view)
    eligible = [group for group in groups.values() if len({view.view_kind for view in group}) > 1]
    rng = random.Random(seed)
    rng.shuffle(eligible)
    batch: list[TrainingView] = []
    for group in eligible:
        # Never split or truncate an artifact's positive set. A large group may
        # exceed the requested soft batch limit by itself.
        if batch and len(batch) + len(group) > size:
            yield batch
            batch = []
        batch.extend(group)
    if batch:
        yield batch


def train_corpus(root: str | Path, checkpoint: str | Path, *, epochs: int = 5,
                 batch_size: int = 16, seed: int = 0, device: str = "cpu",
                 dimension: int = 256, layers: int = 4) -> dict:
    if epochs < 1:
        raise ValueError("epochs must be positive")
    random.seed(seed)
    torch.manual_seed(seed)
    views = _views(root, "train", semantic_only=True)
    batches = list(_batches(views, batch_size, seed))
    if not batches:
        raise ValueError("no eligible semantic training pairs in the train split")
    if dimension < 8 or layers < 1:
        raise ValueError("dimension must be at least 8 and layers must be positive")
    model = SharedGraphEncoder(dimension=dimension, layers=layers).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    losses: list[float] = []
    for epoch in range(epochs):
        for batch in _batches(views, batch_size, seed + epoch):
            losses.append(train_step(model, optimizer, batch))
    checkpoint = Path(checkpoint)
    checkpoint.parent.mkdir(parents=True, exist_ok=True)
    state = {"format": 2, "model": model.state_dict(), "config": {"dimension": model.dimension,
             "layers": len(model.layers), "node_buckets": model.node_buckets,
             "relation_buckets": model.relation_buckets, "schema_version": SCHEMA_VERSION,
             "feature_keys": list(FEATURE_KEYS), "epochs": epochs, "seed": seed}}
    with tempfile.NamedTemporaryFile(dir=checkpoint.parent, prefix=f".{checkpoint.name}.",
                                     suffix=".tmp", delete=False) as handle:
        temporary = Path(handle.name)
    try:
        torch.save(state, temporary)
        os.replace(temporary, checkpoint)
    finally:
        temporary.unlink(missing_ok=True)
    return {"examples": len(views), "epochs": epochs, "loss": sum(losses) / len(losses), "checkpoint": str(checkpoint)}


def _load_model(checkpoint: str | Path, device: str = "cpu") -> SharedGraphEncoder:
    state = torch.load(checkpoint, map_location=device, weights_only=True)
    config = state.get("config", {})
    if state.get("format") != 2 or config.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("checkpoint is incompatible with the current graph schema")
    if config.get("feature_keys") != list(FEATURE_KEYS):
        raise ValueError("checkpoint feature profile is incompatible")
    model = SharedGraphEncoder(dimension=config["dimension"], layers=config["layers"],
                               node_buckets=config["node_buckets"],
                               relation_buckets=config["relation_buckets"]).to(device)
    model.load_state_dict(state["model"])
    model.eval()
    return model


def _paired_metrics(vectors: torch.Tensor, views: list[TrainingView], *, ks: tuple[int, ...] = (1, 5, 10),
                    query_indices: list[int] | None = None) -> dict:
    if not views:
        return {"eligible_queries": 0, "status": "no-paired-test-views"}
    similarities = vectors @ vectors.T
    hits = {k: 0 for k in ks}
    reciprocal_ranks: list[float] = []
    possible = 0
    queries = query_indices if query_indices is not None else list(range(len(views)))
    for index in queries:
        view = views[index]
        positives = {other for other, candidate in enumerate(views)
                     if candidate.artifact_id == view.artifact_id and candidate.view_kind != view.view_kind}
        if not positives:
            continue
        possible += 1
        ranked = [value for value in torch.argsort(similarities[index], descending=True).tolist() if value != index]
        for k in ks:
            hits[k] += bool(positives.intersection(ranked[:k]))
        rank = next((position + 1 for position, candidate in enumerate(ranked) if candidate in positives), None)
        if rank is not None:
            reciprocal_ranks.append(1.0 / rank)
    metrics = {f"paired_recall_at_{k}": hits[k] / possible if possible else 0.0 for k in ks}
    return {"eligible_queries": possible, "mrr": sum(reciprocal_ranks) / possible if possible else 0.0,
            "status": "ok" if possible else "no-paired-test-views", **metrics}


def _hashed_graph_vectors(views: list[TrainingView], dimension: int = 512) -> torch.Tensor:
    """Deterministic bag-of-graph-features baseline with no learned weights."""
    rows = torch.zeros((len(views), dimension), dtype=torch.float32)
    for row, view in enumerate(views):
        for node in view.graph.nodes:
            tokens = [f"node:{node.kind}"]
            tokens.extend(f"node:{key}={node.attributes[key]}" for key in FEATURE_KEYS
                          if key in node.attributes)
            for token in tokens:
                rows[row, int.from_bytes(hashlib.blake2b(token.encode(), digest_size=8).digest(), "big") % dimension] += 1
        for edge in view.graph.edges:
            token = f"edge:{edge.kind}:{edge.attributes.get('position', '*')}"
            rows[row, int.from_bytes(hashlib.blake2b(token.encode(), digest_size=8).digest(), "big") % dimension] += 1
    return torch.nn.functional.normalize(rows, dim=-1)


def evaluate_corpus(root: str | Path, checkpoint: str | Path, *, limit: int = 5) -> dict:
    entries = _view_entries(root, "test", semantic_only=True)
    views = [view for view, _ in entries]
    model = _load_model(checkpoint)
    if not views:
        return {"split": "test", "examples": 0, "status": "no-semantic-test-views", "accepts": False}
    with torch.no_grad():
        vectors = model(view.graph for view in views)
    ks = tuple(sorted({1, limit, 10}))
    metrics = _paired_metrics(vectors, views, ks=ks)
    def slices(key: str, default: str) -> dict:
        result = {}
        for value in sorted({metadata.get(key, default) for _, metadata in entries}):
            indices = [index for index, (_, metadata) in enumerate(entries) if metadata.get(key, default) == value]
            result[value] = _paired_metrics(vectors, views, ks=ks, query_indices=indices)
        return result
    torch.manual_seed(0)
    untrained = SharedGraphEncoder(dimension=model.dimension, layers=len(model.layers),
                                   node_buckets=model.node_buckets,
                                   relation_buckets=model.relation_buckets)
    with torch.no_grad():
        untrained_vectors = untrained(view.graph for view in views)
    metrics.update({"split": "test", "examples": len(views),
                    "baselines": {
                        "hashed_graph_cosine": _paired_metrics(_hashed_graph_vectors(views), views, ks=ks),
                        "untrained_shared_encoder": _paired_metrics(untrained_vectors, views, ks=ks),
                    },
                    "by_research_tier": slices("research_tier", "standard"),
                    "by_diagnostic_family": slices("diagnostic_family", "transformation"),
                    "accepts": metrics["eligible_queries"] > 0 and
                               metrics[f"paired_recall_at_{limit}"] >= 0.90})
    return metrics


def calibrate_threshold(root: str | Path, checkpoint: str | Path, *, target_precision: float = 0.95,
                        max_negative_pairs: int = 100_000) -> dict:
    """Fit a pair-retrieval threshold on validation data only.

    Different artifacts are proxy negatives, not proof of an unknown family; the
    returned report makes that limitation explicit.
    """
    if not 0 < target_precision <= 1:
        raise ValueError("target precision must be in (0, 1]")
    views = _views(root, "validation", semantic_only=True)
    model = _load_model(checkpoint)
    if len(views) < 2:
        raise ValueError("validation split needs at least two semantic views")
    with torch.no_grad():
        vectors = model(view.graph for view in views)
    similarities = vectors @ vectors.T
    positives: list[float] = []
    negatives: list[float] = []
    for left in range(len(views)):
        for right in range(left + 1, len(views)):
            if views[left].artifact_id == views[right].artifact_id and views[left].view_kind != views[right].view_kind:
                positives.append(float(similarities[left, right]))
            elif len(negatives) < max_negative_pairs:
                negatives.append(float(similarities[left, right]))
    if not positives or not negatives:
        raise ValueError("validation split needs both positive and proxy-negative pairs")
    best: tuple[float, float, float] | None = None
    for threshold in sorted(set(positives + negatives), reverse=True):
        true_positive = sum(score >= threshold for score in positives)
        false_positive = sum(score >= threshold for score in negatives)
        precision = true_positive / max(1, true_positive + false_positive)
        recall = true_positive / len(positives)
        if precision >= target_precision and (best is None or recall > best[2]):
            best = (threshold, precision, recall)
    if best is None:
        return {"status": "inconclusive", "target_precision": target_precision,
                "positive_pairs": len(positives), "proxy_negative_pairs": len(negatives)}
    return {"status": "calibrated_proxy_pairs", "threshold": best[0], "precision": best[1],
            "recall": best[2], "target_precision": target_precision,
            "positive_pairs": len(positives), "proxy_negative_pairs": len(negatives),
            "limitation": "different validation artifacts are proxy negatives, not novel-family ground truth"}


def write_benchmark_report(root: str | Path, checkpoint: str | Path, output: str | Path) -> dict:
    result = evaluate_corpus(root, checkpoint)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return {"report": str(output), **result}


def index_corpus(root: str | Path, checkpoint: str | Path, directory: str | Path) -> dict:
    entries = _view_entries(root, semantic_only=True)
    entries = [(view, metadata) for view, metadata in entries if view.view_kind == "source"]
    model = _load_model(checkpoint)
    grouped: dict[str, list[tuple[TrainingView, dict]]] = defaultdict(list)
    for view, metadata in entries:
        grouped[metadata["source_artifact_id"]].append((view, metadata))
    records: list[EmbeddingRecord] = []
    with torch.no_grad():
        for source_id, units in grouped.items():
            unit_vectors = model(item[0].graph for item in units)
            vector = torch.nn.functional.normalize(unit_vectors.mean(dim=0), dim=0).tolist()
            metadata = dict(units[0][1])
            metadata.update({"source_artifact_id": source_id, "unit_count": len(units),
                             "origin": units[0][0].graph.metadata.get("origin")})
            records.append(EmbeddingRecord(source_id, vector, metadata))
    fingerprint = _model_fingerprint(checkpoint)
    index = LocalFaissIndex(directory, model.dimension, fingerprint=fingerprint)
    index.upsert(records)
    return {"indexed": len(records), "directory": str(directory), "fingerprint": fingerprint,
            "granularity": "source_file"}


def _model_fingerprint(checkpoint: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(checkpoint).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    digest.update(f"schema={SCHEMA_VERSION}|features={','.join(FEATURE_KEYS)}".encode())
    return digest.hexdigest()


def search_artifact(path: str | Path, checkpoint: str | Path, directory: str | Path,
                    limit: int = 10, threshold: float = 0.80) -> dict:
    from .ingest import ingest_path
    model = _load_model(checkpoint)
    result = ingest_path(path)
    with torch.no_grad():
        unit_vectors = model(graph for graph in result.graphs)
        vector = torch.nn.functional.normalize(unit_vectors.mean(dim=0), dim=0).tolist()
    index = LocalFaissIndex(directory, model.dimension,
                            fingerprint=_model_fingerprint(checkpoint))
    hits = index.search_scored(vector, limit=limit)
    exact_hash = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    exact_record = next((record for record in index.records()
                         if record.metadata.get("exact_source_hash") == exact_hash), None)
    structural_record = None
    if Path(path).suffix != ".pyc":
        structural = canonical_hash(Path(path).read_text(encoding="utf-8", errors="replace"))
        structural_record = next((record for record in index.records()
                                  if record.metadata.get("structural_source_hash") == structural), None)
    best = hits[0] if hits else None
    if exact_record is not None:
        status, confidence = "matched", "exact"
    elif structural_record is not None:
        status, confidence = "matched", "structural"
    elif result.lane == "recovery":
        status, confidence = "insufficient_evidence", "low"
    elif best is not None and best.score >= threshold:
        status, confidence = "matched", "embedding"
    else:
        status, confidence = "unknown", "below_threshold"
    return {"status": status, "confidence": confidence, "lane": result.lane,
            "threshold": threshold, "best_score": best.score if best else None,
            "baseline_match_id": (exact_record or structural_record).id
                                 if exact_record or structural_record else None,
            "candidates": [{"id": hit.record.id, "score": hit.score,
                            "metadata": hit.record.metadata} for hit in hits]}


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
