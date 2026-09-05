"""Safe, cross-lane program-graph ingestion and embedding utilities."""

from .ingest import IngestionResult, ingest_path, ingest_source
from .semantic import ProgramGraph
from .shared_model import SharedGraphEncoder

__all__ = ["IngestionResult", "ProgramGraph", "SharedGraphEncoder", "ingest_path", "ingest_source"]
