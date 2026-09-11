"""Development-only diagnosis; never score or execute the reserved test split."""
from __future__ import annotations

import ast
from collections import Counter
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import platform
import tokenize

import torch

from .ingest import ingest_source
from .shared_model import FEATURE_KEYS, SharedGraphEncoder, graph_tensors
from .training import TrainingView
from .workflow import _hashed_graph_vectors, _load_model

ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "hardpairs"
METHODS = ("trained", "untrained", "hashed_graph", "tokens", "operation_api")


def fingerprint(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def load_manifest(root: Path = ROOT) -> dict:
    data = json.loads((root / "manifest.json").read_text())
    families, owners, paths = set(), {}, set()
    for row in data["families"]:
        if row["family"] in families or row["split"] not in {"train", "validation", "test"}:
            raise ValueError("duplicate family or invalid split")
        families.add(row["family"])
        for relative in [*row["variants"].values(), row["oracle"]]:
            path = (root / relative).resolve()
            if not path.is_relative_to(root.resolve()) or relative in paths:
                raise ValueError("unsafe or shared fixture path")
            paths.add(relative)
        for kind, relative in row["variants"].items():
            source = (root / relative).read_text()
            # Test sources are parsed only for static integrity/leakage checks.
            keys = (fingerprint(source), fingerprint(ast.dump(ast.parse(source))))
            for key in keys:
                if key in owners and owners[key] != row["family"]:
                    raise ValueError("cross-family exact/AST duplicate")
                owners[key] = row["family"]
            if kind != "original":
                expected = {"related_code": True, "behavior_preserved": kind == "positive"}
                if row["relations"][kind] != expected:
                    raise ValueError("invalid task relation")
    return data


def verify_lock(root: Path = ROOT) -> str:
    path = root / "lock.json"
    lock = json.loads(path.read_text())
    manifest = json.loads((root / "manifest.json").read_text())
    expected = {"manifest.json"}
    for row in manifest["families"]:
        expected.update(row["variants"].values())
        expected.add(row["oracle"])
    if set(lock["sha256"]) != expected:
        raise ValueError("fixture lock inventory differs from manifest")
    for relative, digest in lock["sha256"].items():
        target = (root / relative).resolve()
        if not target.is_relative_to(root.resolve()):
            raise ValueError("unsafe lock path")
        if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise ValueError("fixture checksum mismatch: " + relative)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_owned(row: dict, root: Path = ROOT) -> dict:
    if row["split"] == "test":
        raise ValueError("reserved test family: execution and scoring forbidden")
    cases = json.loads((root / row["oracle"]).read_text())
    results = {}
    for kind, relative in row["variants"].items():
        # Only repository-owned first-party fixture code, never corpus code.
        namespace = {}
        exec(compile((root / relative).read_text(), relative, "exec"), namespace)
        outcomes = []
        for case in cases:
            try:
                actual = namespace["run"](deepcopy(case["input"]))
                outcomes.append(actual == case.get("expected") and "error" not in case)
            except Exception as error:
                outcomes.append(type(error).__name__ == case.get("error"))
        results[kind] = outcomes
        if not cases or (all(outcomes) != (kind != "negative")):
            raise ValueError("oracle relation failed: " + row["family"] + "/" + kind)
    return results


def sparse_features(source: str, method: str) -> Counter:
    if method == "tokens":
        ignored = {tokenize.ENCODING, tokenize.ENDMARKER, tokenize.INDENT, tokenize.DEDENT,
                   tokenize.NEWLINE, tokenize.NL, tokenize.COMMENT}
        return Counter(str(t.type) + ":" + t.string for t in tokenize.generate_tokens(
            io.StringIO(source).readline) if t.type not in ignored)
    result = Counter()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.operator, ast.unaryop, ast.boolop, ast.cmpop)):
            result["op:" + type(node).__name__] += 1
        elif isinstance(node, ast.Call):
            result["call:" + ast.unparse(node.func)] += 1
        elif isinstance(node, ast.Constant):
            result["literal:" + type(node.value).__name__ + ":" + repr(node.value)] += 1
        elif isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.Raise, ast.Return)):
            result["control:" + type(node).__name__] += 1
    return result


def cosine(a, b) -> float:
    if isinstance(a, Counter):
        norm = sum(x*x for x in a.values()) * sum(x*x for x in b.values())
        return sum(x*b.get(k, 0) for k, x in a.items()) / norm**0.5 if norm else 0.0
    return max(-1.0, min(1.0, float(a @ b)))


def facts(graph, model) -> dict:
    positions = {node.id: i for i, node in enumerate(graph.nodes)}
    ignored = {"line", "column", "end_line", "end_column"}
    graph_evidence = {
        "nodes": [(n.kind, {k: v for k, v in n.attributes.items() if k not in ignored})
                  for n in graph.nodes],
        "edges": [(positions[e.source], positions[e.target], e.kind, e.attributes) for e in graph.edges],
    }
    tokens = [["kind=" + n.kind, *[f"{k}={n.attributes[k]}" for k in FEATURE_KEYS if k in n.attributes]]
              for n in graph.nodes]
    edges = [(positions[e.source], positions[e.target],
              f"{e.kind}|position={e.attributes.get('position', '*')}") for e in graph.edges]
    tensors = graph_tensors(graph, node_buckets=model.node_buckets,
                            relation_buckets=model.relation_buckets)
    return {"graph": fingerprint(graph_evidence), "selected_features": fingerprint([tokens, edges]),
            "tensors": fingerprint({k: v.tolist() for k, v in tensors.items() if k != "availability"})}


def trace(graph, model):
    """Observe the actual encoder, rather than implementing a second forward pass."""
    stages, handles = {}, []
    def capture(name):
        def hook(module, args, output):
            stages[name] = output.detach().clone()
        return hook
    for index, layer in enumerate(model.layers):
        handles.append(layer.register_forward_hook(capture("layer_" + str(index))))
    def pooled(module, args):
        stages["node_mean"] = args[0].detach().clone()
    handles.append(model.project.register_forward_pre_hook(pooled))
    try:
        vector = model.encode_graph(graph)
    finally:
        for handle in handles:
            handle.remove()
    stages["unit_vector"] = vector.detach().clone()
    return vector, stages


def diagnose(checkpoint: str | Path, output: str | Path, *, split: str = "train",
             root: Path = ROOT) -> dict:
    if split not in {"train", "validation"}:
        raise ValueError("diagnostics permit only train or validation; test is reserved")
    output = Path(output)
    if output.exists():
        raise ValueError("choose a new diagnostic output directory")
    manifest = load_manifest(root)
    lock_hash = verify_lock(root)
    selected = [r for r in manifest["families"] if r["split"] == split]
    trained = _load_model(checkpoint)
    torch.manual_seed(0)
    untrained = SharedGraphEncoder(dimension=trained.dimension, layers=len(trained.layers),
                                  node_buckets=trained.node_buckets,
                                  relation_buckets=trained.relation_buckets).eval()
    cache, oracles, file_hashes = {}, {}, {}
    with torch.no_grad():
        for row in selected:
            oracles[row["family"]] = verify_owned(row, root)
            for kind, relative in row["variants"].items():
                source = (root / relative).read_text()
                file_hashes[relative] = hashlib.sha256(source.encode()).hexdigest()
                graphs = ingest_source(source, origin=relative).graphs
                units = {g.metadata["qualified_name"]: g for g in graphs}
                if len(units) != len(graphs):
                    raise ValueError("ambiguous unit lineage")
                record = {"units": units, "facts": {n: facts(g, trained) for n, g in units.items()},
                          "vectors": {}, "unit_vectors": {}, "traces": {}}
                for method, model in (("trained", trained), ("untrained", untrained)):
                    records = {n: trace(g, model) for n, g in units.items()}
                    record["unit_vectors"][method] = {n: v for n, (v, _) in records.items()}
                    record["traces"][method] = {n: t for n, (_, t) in records.items()}
                    record["vectors"][method] = torch.nn.functional.normalize(
                        torch.stack([v for v, _ in records.values()]).mean(0), dim=0)
                hashed = _hashed_graph_vectors([TrainingView(g, "", "") for g in graphs])
                record["vectors"]["hashed_graph"] = torch.nn.functional.normalize(hashed.mean(0), dim=0)
                for method in ("tokens", "operation_api"):
                    record["vectors"][method] = sparse_features(source, method)
                cache[(row["family"], kind)] = record

    failures, retrieval, pairs = [], [], []
    for row in selected:
        family = row["family"]
        a, b = cache[(family, "original")], cache[(family, "negative")]
        unit_rows = []
        for name in sorted(set(a["units"]) | set(b["units"])):
            if name not in a["units"] or name not in b["units"]:
                unit_rows.append({"unit": name, "lineage": "unmatched"})
                continue
            same = {k: a["facts"][name][k] == b["facts"][name][k] for k in a["facts"][name]}
            distances = {}
            for method in ("trained", "untrained"):
                distances[method] = {}
                for stage, va in a["traces"][method][name].items():
                    vb = b["traces"][method][name][stage]
                    distances[method][stage] = float(torch.linalg.vector_norm(va-vb)) if va.shape == vb.shape else None
            unit_rows.append({"unit": name, "lineage": "qualified_name", "identical": same,
                              "stage_l2": distances})
        same_graph = a["facts"].keys() == b["facts"].keys() and all(
            a["facts"][n]["graph"] == b["facts"][n]["graph"] for n in a["facts"])
        same_features = a["facts"].keys() == b["facts"].keys() and all(
            a["facts"][n]["selected_features"] == b["facts"][n]["selected_features"] for n in a["facts"])
        same_tensors = a["facts"].keys() == b["facts"].keys() and all(
            a["facts"][n]["tensors"] == b["facts"][n]["tensors"] for n in a["facts"])
        file_l2 = float(torch.linalg.vector_norm(a["vectors"]["trained"]-b["vectors"]["trained"]))
        maximum = max((u["stage_l2"]["trained"]["unit_vector"] for u in unit_rows if "stage_l2" in u), default=0)
        cause = ("normalization_loss" if same_graph else "feature_selection_loss" if same_features else
                 "hash_collision" if same_tensors else "encoder_invariance" if maximum <= 1e-6 else
                 "observable_change")
        failures.append({"family": family, "change": row["change"], "earliest_loss": cause,
                         "file_l2": file_l2, "max_unit_l2": maximum,
                         "pooling_dilution": maximum > 1e-6 and file_l2 < maximum * 0.5,
                         "units": unit_rows})
        for left, right in (("original", "positive"), ("original", "negative"), ("positive", "negative")):
            pairs.append({"family": family, "left": left, "right": right,
                          "cosine": {m: cosine(cache[(family,left)]["vectors"][m],
                                               cache[(family,right)]["vectors"][m]) for m in METHODS}})
        for method in METHODS:
            query = cache[(family, "positive")]["vectors"][method]
            gallery = [(r["family"], "original") for r in selected] + [(family, "negative")]
            candidates = [{"family": f, "variant": k,
                           "cosine": cosine(query, cache[(f,k)]["vectors"][method])} for f,k in gallery]
            own = next(c["cosine"] for c in candidates if c["family"] == family and c["variant"] == "original")
            neg = candidates[-1]["cosine"]
            rank = 1 + sum(c["cosine"] >= own-1e-7 for c in candidates
                           if (c["family"],c["variant"]) != (family,"original"))
            # Related-code task allows the mutated near-copy, unlike behavior ranking.
            best_related = max(own, neg)
            related_rank = 1 + sum(c["cosine"] >= best_related-1e-7 for c in candidates if c["family"] != family)
            retrieval.append({"family": family, "method": method, "behavior_rank": rank,
                              "related_rank": related_rank, "positive_margin": own-neg,
                              "candidates": sorted(candidates, key=lambda c: -c["cosine"])})
    summary = {m: {"queries": len(selected),
                   "behavior_top1": sum(r["behavior_rank"] == 1 for r in retrieval if r["method"] == m),
                   "related_top1": sum(r["related_rank"] == 1 for r in retrieval if r["method"] == m)} for m in METHODS}
    report = {"format": 1, "split": split, "test_scored": False, "fixture_lock_sha256": lock_hash, "checkpoint_sha256":
              hashlib.sha256(Path(checkpoint).read_bytes()).hexdigest(), "manifest_sha256":
              hashlib.sha256((root / "manifest.json").read_bytes()).hexdigest(),
              "diagnostic_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "python": platform.python_version(), "torch": torch.__version__,
              "untrained_seed": 0, "file_hashes": file_hashes, "oracles": oracles,
              "summary": summary, "diagnostics": failures, "pairs": pairs, "retrieval": retrieval}
    output.mkdir(parents=True)
    (output / "diagnostics.json").write_text(json.dumps(report, indent=2, sort_keys=True)+"\n")
    lines = ["# Hard-pair development diagnosis", "", "Split: **"+split+"**. Reserved test split was not executed or scored.",
             "", "These are development diagnostics, not final test accuracy. Cosine is not a probability.",
             "", "| Family | Earliest loss | Maximum unit L2 | File L2 | Pooling dilution |",
             "|---|---|---:|---:|---|"]
    lines += [f"| {r['family']} | {r['earliest_loss']} | {r['max_unit_l2']:.8f} | {r['file_l2']:.8f} | {r['pooling_dilution']} |" for r in failures]
    lines += ["", "| Method | Behavior top-1 | Related-code top-1 | Queries |", "|---|---:|---:|---:|"]
    lines += [f"| {m} | {s['behavior_top1']} | {s['related_top1']} | {s['queries']} |" for m,s in summary.items()]
    lines += ["", "See diagnostics.json for per-unit hidden-layer/node-mean distances, raw pair scores, candidate galleries and behavior checks.",
              "Pooling dilution flags file L2 below half the largest unit L2; it is a diagnostic heuristic, not a causal proof.",
              "Encoder invariance uses unit-vector L2 <= 1e-6. Static graph fingerprints exclude source coordinates."]
    (output / "report.md").write_text("\n".join(lines)+"\n")
    return {"output": str(output), "split": split, "summary": summary,
            "losses": dict(Counter(r["earliest_loss"] for r in failures)), "test_scored": False}
