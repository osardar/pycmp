"""Library-friendly command line workflows for the shared embedding corpus."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch

from .corpus import EmbeddingRecord, LocalFaissIndex
from .corpus_builder import build_corpus
from .decompile import decompile_pyc
from .ingest import ingest_path
from .semantic import ProgramGraph
from .shared_model import SharedGraphEncoder
from .workflow import evaluate_corpus, export_vertex, index_corpus, search_artifact, train_corpus


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
    corpus = commands.add_parser("corpus")
    corpus_commands = corpus.add_subparsers(dest="corpus_command", required=True)
    build = corpus_commands.add_parser("build")
    build.add_argument("manifest")
    build.add_argument("--output", required=True)
    train = commands.add_parser("train")
    train.add_argument("corpus")
    train.add_argument("--checkpoint", required=True)
    train.add_argument("--epochs", type=int, default=5)
    train.add_argument("--batch-size", type=int, default=16)
    train.add_argument("--device", default="cpu")
    evaluate = commands.add_parser("evaluate")
    evaluate.add_argument("corpus")
    evaluate.add_argument("--checkpoint", required=True)
    corpus_index = commands.add_parser("corpus-index")
    corpus_index.add_argument("corpus")
    corpus_index.add_argument("--checkpoint", required=True)
    corpus_index.add_argument("--directory", required=True)
    search = commands.add_parser("search")
    search.add_argument("input")
    search.add_argument("--checkpoint", required=True)
    search.add_argument("--directory", required=True)
    search.add_argument("--limit", type=int, default=10)
    export = commands.add_parser("export-vertex")
    export.add_argument("--directory", required=True)
    export.add_argument("--output", required=True)
    export.add_argument("--dimension", type=int, default=256)
    decompile = commands.add_parser("decompile")
    decompile.add_argument("input")
    decompile.add_argument("--backlog", required=True)
    decompile.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    if args.command == "ingest":
        result = ingest_path(args.input, python_minor=args.python_minor, reconstructed=args.reconstructed)
        _save_graphs(result.graphs, Path(args.output))
        print(json.dumps({"lane": result.lane, "units": len(result.graphs), "diagnostics": result.diagnostics}))
        return 0
    if args.command == "corpus":
        print(json.dumps(build_corpus(args.manifest, args.output), sort_keys=True))
        return 0
    if args.command == "train":
        print(json.dumps(train_corpus(args.corpus, args.checkpoint, epochs=args.epochs,
                                      batch_size=args.batch_size, device=args.device), sort_keys=True))
        return 0
    if args.command == "evaluate":
        print(json.dumps(evaluate_corpus(args.corpus, args.checkpoint), sort_keys=True))
        return 0
    if args.command == "corpus-index":
        print(json.dumps(index_corpus(args.corpus, args.checkpoint, args.directory), sort_keys=True))
        return 0
    if args.command == "search":
        print(json.dumps(search_artifact(args.input, args.checkpoint, args.directory, args.limit), sort_keys=True))
        return 0
    if args.command == "export-vertex":
        print(json.dumps(export_vertex(args.directory, args.output, args.dimension), sort_keys=True))
        return 0
    if args.command == "decompile":
        result = decompile_pyc(args.input, backlog_path=args.backlog)
        if result is None:
            print(json.dumps({"status": "gap-recorded"}))
            return 2
        _save_graphs(result.graphs, Path(args.output))
        print(json.dumps({"status": "ok", "lane": result.lane, "units": len(result.graphs)}))
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
