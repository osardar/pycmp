"""Library-friendly command line workflows for the shared embedding corpus."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch

from .corpus import EmbeddingRecord, LocalFaissIndex
from .ingest import ingest_path
from .semantic import ProgramGraph
from .shared_model import SharedGraphEncoder


def _save_graphs(graphs: list[ProgramGraph], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(json.dumps(graph.to_dict(), sort_keys=True) for graph in graphs) + "\n")


def _load_graphs(path: Path) -> list[ProgramGraph]:
    return [ProgramGraph.from_dict(json.loads(line)) for line in path.read_text().splitlines() if line]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="codegraph")
    commands = parser.add_subparsers(dest="command", required=True)
    ingest = commands.add_parser("ingest")
    ingest.add_argument("input")
    ingest.add_argument("--output", required=True)
    ingest.add_argument("--python-minor", type=int)
    ingest.add_argument("--reconstructed", action="store_true")
    embed = commands.add_parser("embed")
    embed.add_argument("graphs")
    embed.add_argument("--checkpoint")
    embed.add_argument("--output", required=True)
    index = commands.add_parser("index")
    index.add_argument("embeddings")
    index.add_argument("--directory", required=True)
    args = parser.parse_args(argv)

    if args.command == "ingest":
        result = ingest_path(args.input, python_minor=args.python_minor, reconstructed=args.reconstructed)
        _save_graphs(result.graphs, Path(args.output))
        print(json.dumps({"lane": result.lane, "units": len(result.graphs), "diagnostics": result.diagnostics}))
        return 0
    if args.command == "embed":
        model = SharedGraphEncoder()
        if args.checkpoint:
            model.load_state_dict(torch.load(args.checkpoint, map_location="cpu", weights_only=True))
        graphs = _load_graphs(Path(args.graphs))
        vectors = model(graphs).detach().tolist()
        Path(args.output).write_text("\n".join(json.dumps({"id": graph.unit_id, "embedding": vector,
                                                              "metadata": graph.metadata})
                                            for graph, vector in zip(graphs, vectors)) + "\n")
        return 0
    records = [EmbeddingRecord(**json.loads(line)) for line in Path(args.embeddings).read_text().splitlines() if line]
    if not records:
        raise ValueError("no embeddings supplied")
    local = LocalFaissIndex(args.directory, len(records[0].embedding))
    local.upsert(records)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
