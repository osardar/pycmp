"""Versioned local corpus records and swappable vector-index backends."""
from __future__ import annotations

import json
import os
import tempfile
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch


@dataclass(frozen=True)
class EmbeddingRecord:
    id: str
    embedding: list[float]
    metadata: dict[str, Any]


@dataclass(frozen=True)
class SearchHit:
    record: EmbeddingRecord
    score: float


class VectorIndex(ABC):
    @abstractmethod
    def upsert(self, records: list[EmbeddingRecord]) -> None: ...

    @abstractmethod
    def search(self, embedding: list[float], limit: int = 10,
               filters: dict[str, Any] | None = None) -> list[EmbeddingRecord]: ...


class LocalFaissIndex(VectorIndex):
    """Reproducible FAISS-backed development index with JSONL metadata."""

    def __init__(self, directory: str | Path, dimension: int, *, fingerprint: str | None = None) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.dimension = dimension
        self.records_path = self.directory / "records.jsonl"
        self.manifest_path = self.directory / "index-manifest.json"
        self.fingerprint = fingerprint
        if self.manifest_path.exists():
            manifest = json.loads(self.manifest_path.read_text())
            if manifest.get("dimension") != dimension:
                raise ValueError("index dimension is incompatible")
            if fingerprint is not None and manifest.get("fingerprint") != fingerprint:
                raise ValueError("index model/preprocessing fingerprint is incompatible")
        elif fingerprint is not None:
            self._atomic_write(self.manifest_path, json.dumps(
                {"format": 1, "dimension": dimension, "fingerprint": fingerprint},
                indent=2, sort_keys=True) + "\n")
        self._records: dict[str, EmbeddingRecord] = {}
        if self.records_path.exists():
            for line in self.records_path.read_text().splitlines():
                value = EmbeddingRecord(**json.loads(line))
                self._records[value.id] = value

    @staticmethod
    def _atomic_write(path: Path, value: str) -> None:
        descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(value)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_name, path)
        finally:
            Path(temporary_name).unlink(missing_ok=True)

    def _write(self) -> None:
        self._atomic_write(self.records_path, "".join(
            json.dumps(record.__dict__, sort_keys=True) + "\n"
            for record in sorted(self._records.values(), key=lambda item: item.id)))

    def records(self) -> list[EmbeddingRecord]:
        return list(self._records.values())

    def upsert(self, records: list[EmbeddingRecord]) -> None:
        for record in records:
            if len(record.embedding) != self.dimension:
                raise ValueError("embedding dimension does not match index")
            if not all(math.isfinite(value) for value in record.embedding):
                raise ValueError("embedding contains a non-finite value")
            self._records[record.id] = record
        self._write()

    def search(self, embedding: list[float], limit: int = 10,
               filters: dict[str, Any] | None = None) -> list[EmbeddingRecord]:
        return [hit.record for hit in self.search_scored(embedding, limit=limit, filters=filters)]

    def search_scored(self, embedding: list[float], limit: int = 10,
                      filters: dict[str, Any] | None = None) -> list[SearchHit]:
        if limit < 1:
            raise ValueError("search limit must be positive")
        if len(embedding) != self.dimension:
            raise ValueError("query dimension does not match index")
        if not all(math.isfinite(value) for value in embedding):
            raise ValueError("query contains a non-finite value")
        query = torch.tensor(embedding, dtype=torch.float32)
        query = query / query.norm().clamp_min(1e-12)
        candidates = [record for record in self._records.values()
                      if not filters or all(record.metadata.get(k) == v for k, v in filters.items())]
        # FAISS is optional at library-install time, but when present this is the
        # local ANN path. The exact JSONL records remain the portability layer.
        if not filters:
            try:
                import faiss  # type: ignore[import-not-found]
                import numpy as np
                matrix = np.asarray([record.embedding for record in candidates], dtype="float32")
                if len(matrix):
                    faiss.normalize_L2(matrix)
                    index = faiss.IndexFlatIP(self.dimension)
                    index.add(matrix)
                    query_array = np.asarray([embedding], dtype="float32")
                    faiss.normalize_L2(query_array)
                    scores, positions = index.search(query_array, min(limit, len(candidates)))
                    return [SearchHit(candidates[position], float(score))
                            for score, position in zip(scores[0], positions[0]) if position >= 0]
            except ImportError:
                pass
        scored = []
        for record in candidates:
            vector = torch.tensor(record.embedding, dtype=torch.float32)
            score = float(torch.dot(query, vector / vector.norm().clamp_min(1e-12)))
            scored.append((score, record))
        return [SearchHit(record, score) for score, record in
                sorted(scored, key=lambda item: item[0], reverse=True)[:limit]]


class VertexAIVectorSearchIndex(VectorIndex):
    """Contract-compatible adapter boundary for Vertex AI Vector Search.

    Deployment configuration is intentionally supplied by the application, never
    serialized into corpus artifacts.
    """

    def __init__(self, *, endpoint: str, deployed_index_id: str, dimension: int) -> None:
        self.endpoint, self.deployed_index_id, self.dimension = endpoint, deployed_index_id, dimension

    def _client(self):
        try:
            from google.cloud import aiplatform_v1
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("install google-cloud-aiplatform for Vertex AI Vector Search") from exc
        return aiplatform_v1.MatchServiceClient()

    def upsert(self, records: list[EmbeddingRecord]) -> None:
        raise NotImplementedError("Vertex upserts belong in the configured batch-index deployment workflow")

    def search(self, embedding: list[float], limit: int = 10,
               filters: dict[str, Any] | None = None) -> list[EmbeddingRecord]:
        raise NotImplementedError("configure the application-specific Vertex metadata and datapoint mapping")
