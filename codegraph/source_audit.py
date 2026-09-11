"""Reproducible schema-3 evidence audit and untrained, one-factor ablations."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import platform

import torch

from .hardpair_diagnostics import ROOT, facts, fingerprint, load_manifest, verify_lock, verify_owned
from .ingest import ingest_source
from .semantic import GraphEdge, SCHEMA_VERSION
from .shared_model import RelationalLayer, SharedGraphEncoder
from .source_evidence import field_inventory


class ConditionedLayer(RelationalLayer):
    """Experiment only: associate each source message with its relation."""
    def forward(self, values, edge_index, relation):
        if edge_index.numel() == 0:
            return super().forward(values, edge_index, relation)
        source, target = edge_index.unbind(dim=1)
        messages = values[source] * (1 + torch.tanh(relation)) + relation
        aggregate = torch.zeros_like(values)
        aggregate.index_add_(0, target, messages)
        degree = torch.zeros(values.shape[0], 1, device=values.device)
        degree.index_add_(0, target, torch.ones((target.shape[0], 1), device=values.device))
        return self.update(torch.cat((values, aggregate / degree.clamp_min(1)), dim=-1))


def reverse_ast(graph):
    graph = deepcopy(graph)
    graph.edges += [GraphEdge(e.target, e.source, "reverse:"+e.kind, e.available, e.attributes)
                    for e in graph.edges if e.kind.startswith("ast_field:")]
    graph.validate()
    return graph


def pool_score(left, right, method):
    if method == "unit_matching":
        scores = left @ right.T
        # Symmetric coverage: every unit contributes, including unmatched ones.
        return float((scores.max(dim=0).values.mean() + scores.max(dim=1).values.mean()) / 2)
    a = torch.nn.functional.normalize(left.mean(0), dim=0)
    b = torch.nn.functional.normalize(right.mean(0), dim=0)
    return float(a @ b)


def audit(output: str | Path) -> dict:
    output = Path(output)
    if output.exists():
        raise ValueError("choose a new audit directory")
    manifest = load_manifest()
    lock = verify_lock()
    rows = [r for r in manifest["families"] if r["split"] == "train"]
    inputs, oracles, hashes = {}, {}, {}
    for row in rows:
        oracles[row["family"]] = verify_owned(row)
        for kind, relative in row["variants"].items():
            source = (ROOT / relative).read_text()
            hashes[relative] = hashlib.sha256(source.encode()).hexdigest()
            inputs[(row["family"], kind)] = ingest_source(source, origin=relative).graphs
    torch.manual_seed(0)
    base = SharedGraphEncoder(dimension=64, layers=2).eval()
    evidence = []
    for row in rows:
        a, b = [inputs[(row["family"], k)] for k in ("original", "negative")]
        fa, fb = [[facts(g, base) for g in graphs] for graphs in (a, b)]
        evidence.append({"family": row["family"], "original_units": len(a), "negative_units": len(b),
                         "graph_changed": [x["graph"] for x in fa] != [x["graph"] for x in fb],
                         "features_changed": [x["selected_features"] for x in fa] != [x["selected_features"] for x in fb],
                         "tensors_changed": [x["tensors"] for x in fa] != [x["tensors"] for x in fb],
                         "original_facts": fa, "negative_facts": fb})
    experiments = []
    with torch.no_grad():
        for seed in (0, 1, 2):
            torch.manual_seed(seed)
            base = SharedGraphEncoder(dimension=64, layers=2).eval()
            for variant in ("baseline", "reverse_ast", "conditioned_relation", "unit_matching"):
                model = deepcopy(base)
                if variant == "conditioned_relation":
                    model.layers = torch.nn.ModuleList([ConditionedLayer(64) for _ in base.layers])
                    model.load_state_dict(base.state_dict())
                vectors = {key: model([reverse_ast(g) for g in graphs] if variant == "reverse_ast" else graphs)
                           for key, graphs in inputs.items()}
                results = []
                for row in rows:
                    family = row["family"]
                    query = vectors[(family, "positive")]
                    gallery = [(r["family"], "original") for r in rows] + [(family, "negative")]
                    scores = [(f, k, pool_score(query, vectors[(f,k)], variant)) for f,k in gallery]
                    positive = next(s for f,k,s in scores if (f,k) == (family,"original"))
                    negative = scores[-1][2]
                    rank = 1 + sum(s >= positive-1e-7 for f,k,s in scores if (f,k) != (family,"original"))
                    results.append({"family": family, "behavior_rank": rank, "margin": positive-negative,
                                    "candidates": scores})
                experiments.append({"seed": seed, "variant": variant, "trained": False,
                                    "initial_weights_hash": fingerprint({k:v.tolist() for k,v in base.state_dict().items()}),
                                    "queries": len(rows), "top1": sum(r["behavior_rank"] == 1 for r in results),
                                    "mean_margin": sum(r["margin"] for r in results)/len(results), "results": results})
    report = {"schema": SCHEMA_VERSION, "fixture_lock": lock, "python": platform.python_version(),
              "torch": torch.__version__, "split": "train", "test_scored": False, "trained": False,
              "source_hashes": hashes, "oracles": oracles, "evidence": evidence,
              "experiments": experiments,
              "code_hashes": {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                              for name in ("source_audit.py", "source_evidence.py", "ast_normalize.py", "shared_model.py")}}
    output.mkdir(parents=True)
    (output / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True)+"\n")
    (output / "ast-field-inventory.json").write_text(json.dumps(field_inventory(), indent=2)+"\n")
    lines = ["# Schema-3 source evidence audit", "", "Development only; all encoders are untrained. No reserved test scoring.",
             "", "| Family | Graph changed | Selected features changed | Tensors changed |", "|---|---|---|---|"]
    lines += [f"| {r['family']} | {r['graph_changed']} | {r['features_changed']} | {r['tensors_changed']} |" for r in evidence]
    lines += ["", "## One-factor architecture probes", "",
              "Identical initial weights and galleries within each seed. No trained-quality claim or architecture selection.",
              "", "| Seed | Variant | Behavior top-1 / 8 | Mean margin |", "|---:|---|---:|---:|"]
    lines += [f"| {r['seed']} | {r['variant']} | {r['top1']} | {r['mean_margin']:.6f} |" for r in experiments]
    (output / "report.md").write_text("\n".join(lines)+"\n")
    return {"output": str(output), "mutations_observable": sum(r["tensors_changed"] for r in evidence),
            "mutations": len(evidence), "experiments": len(experiments), "trained": False, "test_scored": False}
