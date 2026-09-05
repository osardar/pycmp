"""Safe dispatch across source, reconstruction, and bytecode ingestion lanes."""
from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from .ast_normalize import ASTNormalizer
from .recovery import recovery_graph
from .semantic import ProgramGraph


@dataclass
class IngestionResult:
    graphs: list[ProgramGraph]
    lane: str
    diagnostics: list[str]


def ingest_source(
    source: str | bytes, *, origin: str = "<memory>", python_minor: int | None = None,
    reconstructed: bool = False,
) -> IngestionResult:
    raw = source.encode("utf-8") if isinstance(source, str) else source
    text = raw.decode("utf-8", errors="replace")
    metadata = {"reconstructed": reconstructed}
    try:
        graphs = ASTNormalizer().function_graphs(text, origin=origin, python_minor=python_minor,
                                                 extra_metadata=metadata)
        return IngestionResult(graphs, "ast", [])
    except (SyntaxError, ValueError) as exc:
        graph = recovery_graph(raw, origin=origin, reason=str(exc))
        graph.metadata.update(metadata)
        return IngestionResult([graph], "recovery", [str(exc)])


def ingest_pyc(path: str | Path, *, timeout_seconds: int = 10) -> IngestionResult:
    """Decode a `.pyc` only in a separate constrained interpreter process."""
    pyc_path = Path(path).resolve()
    worker = Path(__file__).with_name("_pyc_worker.py")
    completed = subprocess.run(
        [sys.executable, str(worker), str(pyc_path)],
        check=False, capture_output=True, text=True, timeout=timeout_seconds,
    )
    try:
        response = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("isolated bytecode worker returned invalid output") from exc
    if not response.get("ok"):
        raise ValueError(f"unable to ingest {pyc_path.name}: {response.get('error', 'unknown error')}")
    return IngestionResult([ProgramGraph.from_dict(response["graph"])], "bytecode", [])


def ingest_path(path: str | Path, *, python_minor: int | None = None,
                reconstructed: bool = False) -> IngestionResult:
    path = Path(path)
    if path.suffix == ".pyc":
        return ingest_pyc(path)
    return ingest_source(path.read_bytes(), origin=str(path), python_minor=python_minor,
                         reconstructed=reconstructed)
