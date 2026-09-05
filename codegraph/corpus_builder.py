"""Manifest-driven source corpus construction without executing project code."""
from __future__ import annotations

import fnmatch
import json
import ast
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

from .ingest import ingest_source
from .manifest import CorpusProject, artifact_id, load_manifest, write_lock
from .synthetic import damaged_view, formatted_view, renamed_view


@dataclass(frozen=True)
class CorpusView:
    artifact_id: str
    project: str
    split: str
    view_kind: str
    graph_path: str
    metadata: dict


def _split(name: str) -> str:
    value = int(artifact_id(name)[:8], 16) % 100
    return "train" if value < 80 else "validation" if value < 90 else "test"


def _included(project: CorpusProject, relative: str) -> bool:
    def matches(pattern: str) -> bool:
        return fnmatch.fnmatch(relative, pattern) or (pattern.startswith("**/") and fnmatch.fnmatch(relative, pattern[3:]))
    return any(matches(pattern) for pattern in project.include) and not any(
        matches(pattern) for pattern in project.exclude
    )


def _checkout(project: CorpusProject, checkout_root: Path) -> Path:
    destination = checkout_root / project.name
    if destination.exists():
        return destination
    subprocess.run(["git", "clone", "--no-checkout", project.url, str(destination)], check=True)
    subprocess.run(["git", "-C", str(destination), "checkout", "--detach", project.revision], check=True)
    return destination


def build_corpus(manifest_path: str | Path, output_root: str | Path, *, checkout_root: str | Path | None = None) -> dict:
    projects = load_manifest(manifest_path)
    output = Path(output_root)
    output.mkdir(parents=True, exist_ok=True)
    checkouts = Path(checkout_root) if checkout_root else output / "checkouts"
    graphs_root = output / "graphs"
    records: list[CorpusView] = []
    for project in projects:
        checkout = _checkout(project, checkouts)
        # A project can have separate production and fixture records.  They may
        # never land in different partitions, even when their include patterns
        # do not overlap.
        split = project.partition if project.partition != "auto" else _split(project.split_group or project.name)
        source_paths = sorted(
            path for path in checkout.rglob("*")
            if path.is_file() and path.suffix in project.source_extensions
        )
        for source_path in source_paths:
            relative = source_path.relative_to(checkout).as_posix()
            if not _included(project, relative):
                continue
            source = source_path.read_text(encoding="utf-8", errors="replace")
            source_id = artifact_id(project.name, project.revision, relative)
            variants = [("source", source, {})]
            try:
                # Never discard old-version/invalid fixture input merely because
                # a modern AST cannot safely transform it.
                ast.parse(source)
                variants.extend([
                    ("formatted", formatted_view(source), {}),
                    ("renamed", renamed_view(source, seed_material=source_id), {}),
                ])
            except SyntaxError:
                variants.append(("untransformed", source, {"transform_status": "unsupported_syntax"}))
            variants.append(("damaged", damaged_view(source), {"severity": 1}))
            for view_kind, text, metadata in variants:
                result = ingest_source(text, origin=f"{project.name}/{relative}", reconstructed=view_kind == "damaged")
                file_path = graphs_root / project.name / f"{source_id}.{view_kind}.jsonl"
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text("\n".join(json.dumps(graph.to_dict(), sort_keys=True) for graph in result.graphs) + "\n")
                for position, graph in enumerate(result.graphs):
                    # AST traversal order is stable across the deterministic source
                    # variants, yielding one paired artifact per function/method.
                    unit_artifact_id = artifact_id(source_id, str(position))
                    records.append(CorpusView(unit_artifact_id, project.name, split, view_kind,
                                              str(file_path.relative_to(output)),
                                              {"source_artifact_id": source_id, "unit_id": graph.unit_id,
                                               "lane": result.lane,
                                               "corpus_role": project.corpus_role,
                                               "split_group": project.split_group or project.name,
                                               "source_kind": source_path.suffix,
                                               **metadata}))
    (output / "views.jsonl").write_text("".join(json.dumps(asdict(record), sort_keys=True) + "\n" for record in records))
    write_lock(output / "manifest.lock.json", projects)
    return {"projects": len(projects), "views": len(records), "output": str(output)}
