"""Versioned local corpus records and swappable vector-index backends."""
from __future__ import annotations

import json
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


class VectorIndex(ABC):
    @abstractmethod
    def upsert(self, records: list[EmbeddingRecord]) -> None: ...

    @abstractmethod
    def search(self, embedding: list[float], limit: int = 10,
               filters: dict[str, Any] | None = None) -> list[EmbeddingRecord]: ...


class LocalFaissIndex(VectorIndex):
    """Reproducible FAISS-backed development index with JSONL metadata."""

    def __init__(self, directory: str | Path, dimension: int) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.dimension = dimension
        self.records_path = self.directory / "records.jsonl"
        self._records: dict[str, EmbeddingRecord] = {}
        if self.records_path.exists():
            for line in self.records_path.read_text().splitlines():
                value = EmbeddingRecord(**json.loads(line))
                self._records[value.id] = value

    def _write(self) -> None:
        self.records_path.write_text("".join(json.dumps(record.__dict__, sort_keys=True) + "\n"
                                             for record in self._records.values()))

    def records(self) -> list[EmbeddingRecord]:
        return list(self._records.values())

    def upsert(self, records: list[EmbeddingRecord]) -> None:
        for record in records:
            if len(record.embedding) != self.dimension:
                raise ValueError("embedding dimension does not match index")
            self._records[record.id] = record
        self._write()

    def search(self, embedding: list[float], limit: int = 10,
               filters: dict[str, Any] | None = None) -> list[EmbeddingRecord]:
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
                    _, positions = index.search(query_array, min(limit, len(candidates)))
                    return [candidates[position] for position in positions[0] if position >= 0]
            except ImportError:
                pass
        scored = []
        for record in candidates:
            vector = torch.tensor(record.embedding, dtype=torch.float32)
            score = float(torch.dot(query, vector / vector.norm().clamp_min(1e-12)))
            scored.append((score, record))
        return [record for _, record in sorted(scored, key=lambda item: item[0], reverse=True)[:limit]]


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
