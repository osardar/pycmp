"""Resumable bytecode-to-bytecode retrieval evaluation over a completed corpus run."""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import random
import time

from .corpus_similarity import (Budget, BudgetExceeded, DEFAULT_SECONDS, TIE_TOLERANCE,
                                _rank, atomic_json, sha)
from .semantic import ProgramGraph


FORMAT = 1
RUNTIME = "3.14"
OPTIMIZATIONS = (0, 1, 2)
DENSE_METHODS = ("trained-seed0", "trained-seed1", "trained-seed2",
                 "untrained-seed0", "hashed_graph")
METHODS = (*DENSE_METHODS, "opcode_structure")
EXPECTED_GALLERY = 179
EXPECTED_QUERIES = {0: 5284, 1: 5209, 2: 5209}
RECIPE_FIELDS = ("family", "seed", "requested_dose", "actual_dose",
                 "actual_edit_count", "status", "reason")


def _fingerprint(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def _direct_inventory(input_run: Path) -> dict:
    rows = [json.loads(line) for line in
            (input_run / "jobs" / "compiled-lanes.jsonl").read_text().splitlines()]
    inventory = []
    for row in rows:
        if row.get("decode", {}).get("status") != "decoded":
            continue
        artifact = row["artifact_sha256"]
        graph_path = input_run / row["decode"]["graph_path"]
        cache_path = input_run / "embedding-cache" / "lanes" / f"{_direct_cache_key(artifact)}.json"
        if not graph_path.is_file() or not cache_path.is_file():
            raise ValueError("accepted bytecode graph/cache is missing: " + artifact)
        inventory.append((artifact, sha(graph_path), sha(cache_path)))
    return {"artifacts": len(inventory), "sha256": _fingerprint(sorted(inventory))}


def _definition(input_run: Path, checkpoints: list[Path]) -> dict:
    required = ["definition.json", "BUILD-expansion-COMPLETE.json",
                "EVALUATION-expansion-COMPLETE.json", "jobs/compile.jsonl",
                "jobs/compiled-lanes.jsonl", "variant-provenance-expansion.json"]
    for relative in required:
        if not (input_run / relative).is_file():
            raise ValueError(f"completed expansion input is missing {relative}")
    parent = json.loads((input_run / "definition.json").read_text())
    if parent.get("phase") != "expansion" or parent.get("reserved_hardpair_families_accessed") is not False:
        raise ValueError("input must be the completed expansion with reserved families untouched")
    expected = parent["preflight"]["checkpoints"]
    actual = [{"path": str(path.resolve()), "sha256": sha(path)} for path in checkpoints]
    if [row["sha256"] for row in actual] != [row["sha256"] for row in expected]:
        raise ValueError("checkpoint mismatch")
    implementation_files = (Path(__file__), Path(__file__).with_name("corpus_similarity.py"),
                            Path(__file__).with_name("shared_model.py"),
                            Path(__file__).with_name("hardpair_diagnostics.py"))
    return {
        "format": FORMAT,
        "experiment": "bytecode-to-bytecode-lineage-retrieval",
        "input_run": str(input_run.resolve()),
        "input_fingerprints": {relative: sha(input_run / relative) for relative in required},
        "implementation": {path.name: sha(path) for path in implementation_files},
        "direct_artifact_inventory": _direct_inventory(input_run),
        "checkpoints": actual,
        "runtime": RUNTIME,
        "query_optimizations": list(OPTIMIZATIONS),
        "gallery_optimizations": list(OPTIMIZATIONS),
        "methods": list(METHODS),
        "tie_tolerance": TIE_TOLERANCE,
        "expected_gallery_per_optimization": EXPECTED_GALLERY,
        "expected_queries_per_optimization": EXPECTED_QUERIES,
        "task": "rank the unchanged compiled original for a related compiled query",
        "boundaries": {
            "executes_corpus_code": False,
            "uses_reconstructions": False,
            "expands_decoder": False,
            "retrains_or_promotes": False,
            "reserved_hardpair_families_accessed": False,
        },
    }


def _prepare_output(output: Path, definition: dict, resume: bool) -> None:
    definition_path = output / "definition.json"
    if definition_path.exists():
        if not resume:
            raise ValueError("output already exists; pass --resume or choose a new directory")
        # Compare canonical JSON so integer mapping keys—which JSON reloads as
        # strings—do not create a false fingerprint mismatch.
        if _fingerprint(json.loads(definition_path.read_text())) != _fingerprint(definition):
            raise ValueError("resume fingerprint mismatch; choose a new output directory")
    else:
        if output.exists() and any(output.iterdir()):
            raise ValueError("nonempty output has no matching definition")
        output.mkdir(parents=True, exist_ok=True)
        atomic_json(definition_path, definition)


def _recipe(row: dict) -> dict:
    return {key: row.get(key) for key in RECIPE_FIELDS}


def build_manifests(compile_rows: list[dict], lane_rows: list[dict],
                    provenance: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    """Derive canonical galleries and artifact-deduplicated queries."""
    lanes = {row["artifact_sha256"]: row for row in lane_rows
             if row.get("decode", {}).get("status") == "decoded"}
    compiled = {(row["source_sha256"], row["runtime"], row["optimization"]): row
                for row in compile_rows if row.get("status") == "compiled"}
    observations: dict[tuple[str, str], dict] = {}
    unchanged: dict[str, dict] = {}
    for row in provenance:
        key = (row["query_gallery_id"], row["variant_sha256"])
        if key not in observations:
            observations[key] = {
                "origin_gallery_id": row["query_gallery_id"],
                "owner": row["owner"],
                "source_sha256": row["variant_sha256"],
                "recipes": [],
            }
        recipe = _recipe(row)
        if recipe not in observations[key]["recipes"]:
            observations[key]["recipes"].append(recipe)
        if row["family"] == "unchanged":
            unchanged[row["query_gallery_id"]] = observations[key]

    galleries = []
    exclusions = []
    valid_origins = set()
    for origin, observation in sorted(unchanged.items()):
        for optimization in OPTIMIZATIONS:
            compile_row = compiled.get((observation["source_sha256"], RUNTIME, optimization))
            if compile_row is None:
                exclusions.append({"kind": "gallery", "origin_gallery_id": origin,
                                   "optimization": optimization, "reason": "compile_gap"})
                continue
            artifact = compile_row["artifact_sha256"]
            lane = lanes.get(artifact)
            if lane is None:
                exclusions.append({"kind": "gallery", "origin_gallery_id": origin,
                                   "optimization": optimization, "artifact_sha256": artifact,
                                   "reason": "decode_not_supported"})
                continue
            galleries.append({"gallery_id": origin, "owner": observation["owner"],
                              "runtime": RUNTIME, "optimization": optimization,
                              "source_sha256": observation["source_sha256"],
                              "artifact_sha256": artifact,
                              "graph_path": lane["decode"]["graph_path"]})
        if sum(row["gallery_id"] == origin for row in galleries) == len(OPTIMIZATIONS):
            valid_origins.add(origin)

    # An origin is eligible only when all three gallery optimization forms are
    # available, keeping the nine cells paired over identical lineages.
    galleries = [row for row in galleries if row["gallery_id"] in valid_origins]
    query_map: dict[tuple[int, str, str], dict] = {}
    for observation in observations.values():
        origin = observation["origin_gallery_id"]
        if origin not in valid_origins:
            exclusions.append({"kind": "query", "origin_gallery_id": origin,
                               "source_sha256": observation["source_sha256"],
                               "reason": "missing_origin"})
            continue
        for optimization in OPTIMIZATIONS:
            compile_row = compiled.get((observation["source_sha256"], RUNTIME, optimization))
            if compile_row is None:
                exclusions.append({"kind": "query", "origin_gallery_id": origin,
                                   "source_sha256": observation["source_sha256"],
                                   "optimization": optimization, "reason": "compile_gap"})
                continue
            artifact = compile_row["artifact_sha256"]
            lane = lanes.get(artifact)
            if lane is None:
                exclusions.append({"kind": "query", "origin_gallery_id": origin,
                                   "source_sha256": observation["source_sha256"],
                                   "optimization": optimization,
                                   "artifact_sha256": artifact,
                                   "reason": "decode_not_supported"})
                continue
            key = (optimization, origin, artifact)
            if key not in query_map:
                query_map[key] = {
                    "query_id": hashlib.sha256((f"{optimization}\0{origin}\0{artifact}").encode()).hexdigest(),
                    "origin_gallery_id": origin,
                    "owner": observation["owner"],
                    "runtime": RUNTIME,
                    "optimization": optimization,
                    "artifact_sha256": artifact,
                    "graph_path": lane["decode"]["graph_path"],
                    "source_sha256s": [],
                    "recipes": [],
                }
            query = query_map[key]
            if observation["source_sha256"] not in query["source_sha256s"]:
                query["source_sha256s"].append(observation["source_sha256"])
            for recipe in observation["recipes"]:
                if recipe not in query["recipes"]:
                    query["recipes"].append(recipe)
    queries = sorted(query_map.values(), key=lambda row: (row["optimization"], row["query_id"]))
    for row in queries:
        row["source_sha256s"].sort()
        row["recipes"].sort(key=_fingerprint)
    return sorted(galleries, key=lambda row: (row["optimization"], row["gallery_id"])), queries, exclusions


def opcode_structure(graph: ProgramGraph) -> Counter:
    """Transparent bytecode baseline over decoded operations and control edges."""
    result = Counter()
    nodes = {node.id: node for node in graph.nodes}
    for node in graph.nodes:
        opcode = node.attributes.get("opcode")
        if opcode:
            argument = node.attributes.get("argument_kind", "none")
            result[f"opcode:{opcode}"] += 1
            result[f"argument:{argument}"] += 1
            result[f"opcode_argument:{opcode}:{argument}"] += 1
    for edge in graph.edges:
        if not edge.kind.startswith("control_"):
            continue
        source = nodes[edge.source].attributes.get("opcode", "function")
        target = nodes[edge.target].attributes.get("opcode", "function")
        result[f"edge:{edge.kind}"] += 1
        result[f"edge:{edge.kind}:{source}:{target}"] += 1
    return result


def _direct_cache_key(artifact_sha256: str) -> str:
    return hashlib.sha256((artifact_sha256 + "\0bytecode\0direct\0direct").encode()).hexdigest()


def _load_artifact(input_run: Path, row: dict, *, load_graph: bool = True):
    import torch
    cache = input_run / "embedding-cache" / "lanes" / f"{_direct_cache_key(row['artifact_sha256'])}.json"
    if not cache.is_file():
        raise ValueError("missing direct-bytecode embedding cache: " + row["artifact_sha256"])
    value = json.loads(cache.read_text())
    dense = {method: torch.tensor(value["dense"][method]) for method in DENSE_METHODS}
    if not load_graph:
        return dense, None
    graph = ProgramGraph.from_dict(json.loads((input_run / row["graph_path"]).read_text()))
    if graph.metadata.get("parse_status") != "valid" or graph.metadata.get("lane") != "bytecode":
        raise ValueError("invalid direct-bytecode graph: " + row["artifact_sha256"])
    return dense, graph


def _pilot_queries(queries: list[dict]) -> list[dict]:
    selected = {}
    families = ("unchanged", "formatting", "rename", "literal", "operator",
                "structural", "partial", "combined")
    for optimization in OPTIMIZATIONS:
        candidates = [row for row in queries if row["optimization"] == optimization]
        for family in families:
            matching = [row for row in candidates if any(recipe["family"] == family and
                                                          recipe["status"] in {"applied", "unchanged"}
                                                          for recipe in row["recipes"])]
            if not matching:
                raise ValueError(f"pilot has no supported {family} query at optimization {optimization}")
            chosen = min(matching, key=lambda row: hashlib.sha256(
                (family + "\0" + row["query_id"]).encode()).digest())
            selected[chosen["query_id"]] = chosen
    return sorted(selected.values(), key=lambda row: (row["optimization"], row["query_id"]))


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def summarize(rows: list[dict], queries: list[dict], exclusions: list[dict], scope: str,
              coverage: dict) -> dict:
    summary = {}
    for method in METHODS:
        eligible = [row for row in rows if row["scores"][method]["status"] == "ok"]
        summary[method] = {
            "queries": len(eligible),
            **{metric: _mean([float(row["scores"][method][metric]) for row in eligible])
               for metric in ("original_score", "hit_at_1", "hit_at_5", "hit_at_10",
                              "reciprocal_rank", "non_lineage_margin")},
        }
        project_groups = defaultdict(list)
        for row in eligible:
            project_groups[row["owner"]["split_group"]].append(
                row["scores"][method]["reciprocal_rank"])
        summary[method]["project_macro_mrr"] = _mean(
            [_mean(values) for values in project_groups.values()])
    slices = {}
    dimensions = {
        "query_optimization": lambda row: row["query_optimization"],
        "gallery_optimization": lambda row: row["gallery_optimization"],
        "optimization_relation": lambda row: ("same" if row["query_optimization"] ==
                                                row["gallery_optimization"] else "cross"),
        "repository": lambda row: row["owner"]["repository"],
        "split": lambda row: row["owner"]["split"],
    }
    for dimension, getter in dimensions.items():
        groups = defaultdict(list)
        for row in rows:
            groups[str(getter(row))].append(row)
        slices[dimension] = {
            value: {method: {"queries": len(valid),
                             "hit_at_1": _mean([item["scores"][method]["hit_at_1"] for item in valid]),
                             "mrr": _mean([item["scores"][method]["reciprocal_rank"] for item in valid])}
                    for method in METHODS
                    for valid in [[item for item in group if item["scores"][method]["status"] == "ok"]]}
            for value, group in sorted(groups.items())
        }
    family_slices = {}
    for family in sorted({recipe["family"] for query in queries for recipe in query["recipes"]}):
        group = [row for row in rows if any(recipe["family"] == family for recipe in row["recipes"])]
        family_slices[family] = {
            method: {"queries": len(group),
                     "hit_at_1": _mean([item["scores"][method]["hit_at_1"] for item in group]),
                     "mrr": _mean([item["scores"][method]["reciprocal_rank"] for item in group])}
            for method in METHODS}
    dose_slices = {}
    doses = sorted({recipe["actual_dose"] for query in queries for recipe in query["recipes"]
                    if recipe["actual_dose"] is not None})
    for dose in doses:
        group = [row for row in rows if any(recipe["actual_dose"] == dose
                                            for recipe in row["recipes"])]
        dose_slices[str(dose)] = {
            method: {"queries": len(group),
                     "hit_at_1": _mean([item["scores"][method]["hit_at_1"] for item in group]),
                     "mrr": _mean([item["scores"][method]["reciprocal_rank"] for item in group])}
            for method in METHODS}
    paired = {}
    for trained in (f"trained-seed{seed}" for seed in range(3)):
        paired[trained] = {}
        for baseline in ("untrained-seed0", "hashed_graph", "opcode_structure"):
            paired[trained][baseline] = {
                "queries": len(rows),
                "reciprocal_rank_difference": _mean([
                    row["scores"][trained]["reciprocal_rank"] -
                    row["scores"][baseline]["reciprocal_rank"] for row in rows]),
            }
    groups = defaultdict(list)
    for row in rows:
        groups[row["owner"]["split_group"]].append(_mean([
            row["scores"][f"trained-seed{seed}"]["reciprocal_rank"] for seed in range(3)]))
    rng = random.Random(0)
    keys = sorted(groups)
    samples = []
    for _ in range(1000):
        chosen = [rng.choice(keys) for _ in keys]
        samples.append(_mean([_mean(groups[key]) for key in chosen]))
    samples.sort()
    return {
        "format": FORMAT,
        "scope": scope,
        "observations": len(rows),
        "unique_queries": len(queries),
        "methods": summary,
        "slices": {**slices, "family_overlapping": family_slices,
                   "actual_dose_overlapping": dose_slices},
        "paired_trained_minus_baseline": paired,
        "trained_mrr_group_bootstrap_95": [samples[24], samples[974]] if samples else None,
        "exact_binary_matches": sum(row["exact_binary_match"] for row in rows),
        "feature_equal": sum(row["correspondence"]["selected_features"] for row in rows),
        "tensor_equal": sum(row["correspondence"]["tensors"] for row in rows),
        "exclusions": dict(Counter(row["reason"] for row in exclusions)),
        "coverage": coverage,
        "definitions": {"tie_tolerance": TIE_TOLERANCE, "bootstrap_resamples": 1000,
                        "bootstrap_seed": 0, "family_slices_overlap": True,
                        "actual_dose_slices_overlap": True,
                        "not_applicable_methods": ["tokens", "operation_api"],
                        "similarity": "signed cosine, not probability"},
        "limitations": [
            "The candidate gallery has 179 known lineages and is easier than the 2,270-source gallery.",
            "Only Python 3.14 bytecode is decoded; older runtimes remain explicit coverage gaps.",
            "Lineage retrieval does not establish behavioral equivalence, malware classification, or attribution.",
        ],
    }


def render_report(report: dict) -> str:
    def show(value):
        return "N/A" if value is None else f"{value:.4f}"
    lines = ["# Bytecode-to-bytecode similarity evaluation", "",
             f"Scope: **{report['scope']}**. Python 3.14 direct bytecode only; scores are signed cosine values.", "",
             f"Observations: {report['observations']}; unique compiled queries: {report['unique_queries']}.", "",
             "## Retrieval summary", "",
             "| Method | Queries | Cosine | Hit@1 | Hit@5 | Hit@10 | MRR |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for method, row in report["methods"].items():
        lines.append("| %s | %s | %s | %s | %s | %s | %s |" %
                     (method, row["queries"], show(row["original_score"]), show(row["hit_at_1"]),
                      show(row["hit_at_5"]), show(row["hit_at_10"]), show(row["reciprocal_rank"])))
    lines += ["", "## Optimization summary", "",
              "| Relation | Method | Queries | Hit@1 | MRR |", "|---|---|---:|---:|---:|"]
    for relation, methods in report["slices"]["optimization_relation"].items():
        for method, row in methods.items():
            lines.append(f"| {relation} | {method} | {row['queries']} | {show(row['hit_at_1'])} | {show(row['mrr'])} |")
    lines += ["", "## Coverage and interpretation", "",
              f"Exact binary matches: {report['exact_binary_matches']}; selected-feature equality: "
              f"{report['feature_equal']}; tensor equality: {report['tensor_equal']}.", "",
              "Decoder coverage by retained runtime: `" +
              json.dumps(report["coverage"]["decode_by_runtime"], sort_keys=True) + "`.", "",
              "Source token and operation/API baselines are not applicable to direct bytecode. "
              "Family slices in JSON overlap when one compiled artifact represents multiple recipe aliases.", "",
              "## Limitations", ""]
    lines += [f"- {value}" for value in report["limitations"]]
    return "\n".join(lines) + "\n"


def _resume_command(input_run: Path, output: Path, checkpoints: list[Path], max_seconds: int) -> str:
    values = ["uv run pycmp-codegraph corpus-similarity bytecode-evaluate",
              "--input-run", str(input_run), "--output", str(output), "--resume",
              "--max-seconds", str(max_seconds)]
    for checkpoint in checkpoints:
        values += ["--checkpoint", str(checkpoint)]
    return " ".join(values)


def evaluate(input_run: Path, output: Path, checkpoints: list[Path], *, resume: bool = False,
             max_seconds: int = DEFAULT_SECONDS) -> dict:
    import torch
    from .hardpair_diagnostics import facts
    from .workflow import _load_model

    input_run, output = input_run.resolve(), output.resolve()
    if input_run == output:
        raise ValueError("bytecode evaluation output must differ from its input run")
    definition = _definition(input_run, checkpoints)
    _prepare_output(output, definition, resume)
    complete_path = output / "COMPLETE.json"
    if complete_path.exists():
        return json.loads(complete_path.read_text())
    budget = Budget(output, max_seconds, 100 * 1024**3, 8 * 1024**3)
    try:
        compile_rows = [json.loads(line) for line in
                        (input_run / "jobs" / "compile.jsonl").read_text().splitlines()]
        lane_rows = [json.loads(line) for line in
                     (input_run / "jobs" / "compiled-lanes.jsonl").read_text().splitlines()]
        provenance = json.loads((input_run / "variant-provenance-expansion.json").read_text())
        decode_by_runtime = defaultdict(Counter)
        for row in lane_rows:
            decode_by_runtime[row["runtime"]][row["decode"]["status"]] += 1
        compile_by_runtime = defaultdict(Counter)
        for row in compile_rows:
            compile_by_runtime[row["runtime"]][row["status"]] += 1
        coverage = {"decode_by_runtime": {runtime: dict(counts) for runtime, counts in
                                           sorted(decode_by_runtime.items())},
                    "compile_by_runtime": {runtime: dict(counts) for runtime, counts in
                                            sorted(compile_by_runtime.items())}}
        galleries, queries, exclusions = build_manifests(compile_rows, lane_rows, provenance)
        gallery_counts = Counter(row["optimization"] for row in galleries)
        query_counts = Counter(row["optimization"] for row in queries)
        if gallery_counts != Counter({optimization: EXPECTED_GALLERY for optimization in OPTIMIZATIONS}):
            raise ValueError(f"unexpected gallery cardinality: {dict(gallery_counts)}")
        if query_counts != Counter(EXPECTED_QUERIES):
            raise ValueError(f"unexpected query cardinality: {dict(query_counts)}")
        atomic_json(output / "bytecode-gallery.json", galleries, compact=True)
        atomic_json(output / "bytecode-queries.json", queries, compact=True)
        atomic_json(output / "exclusions.json", exclusions, compact=True)

        architecture = _load_model(checkpoints[0]).eval()
        gallery_by_opt = {optimization: [row for row in galleries
                                         if row["optimization"] == optimization]
                          for optimization in OPTIMIZATIONS}
        gallery_vectors = {}
        gallery_facts = {}
        for optimization, candidates in gallery_by_opt.items():
            vectors = defaultdict(list)
            for candidate in candidates:
                budget.check()
                dense, graph = _load_artifact(input_run, candidate)
                for method in DENSE_METHODS:
                    vectors[method].append(dense[method])
                vectors["opcode_structure"].append(opcode_structure(graph))
                gallery_facts[candidate["artifact_sha256"]] = facts(graph, architecture)
            identifiers = [row["gallery_id"] for row in candidates]
            gallery_vectors[optimization] = {
                method: ((identifiers, torch.stack(values)) if method in DENSE_METHODS
                         else list(zip(identifiers, values)))
                for method, values in vectors.items()}

        lineage_ids = defaultdict(set)
        for row in galleries:
            lineage_ids[row["owner"]["split_group"]].add(row["gallery_id"])
        own_gallery = {(row["optimization"], row["gallery_id"]): row for row in galleries}
        artifact_cache = {}
        fact_cache = dict(gallery_facts)

        def artifact_values(query):
            artifact = query["artifact_sha256"]
            if artifact not in artifact_cache:
                dense, graph = _load_artifact(input_run, query)
                dense["opcode_structure"] = opcode_structure(graph)
                artifact_cache[artifact] = dense
                fact_cache[artifact] = facts(graph, architecture)
            return artifact_cache[artifact]

        all_rows = []
        for scope, scoped_queries in (("pilot", _pilot_queries(queries)), ("full", queries)):
            rows = []
            for query in scoped_queries:
                budget.check()
                values = artifact_values(query)
                for gallery_optimization in OPTIMIZATIONS:
                    result_key = hashlib.sha256((query["query_id"] + "\0" +
                                                 str(gallery_optimization)).encode()).hexdigest()
                    result_path = output / "result-cache" / f"{result_key}.json"
                    if result_path.exists():
                        rows.append(json.loads(result_path.read_text()))
                        continue
                    origin = query["origin_gallery_id"]
                    own = own_gallery.get((gallery_optimization, origin))
                    if own is None:
                        result = {**query, "query_optimization": query["optimization"],
                                  "gallery_optimization": gallery_optimization,
                                  "scores": {method: {"status": "missing_origin"} for method in METHODS},
                                  "exact_binary_match": False, "correspondence": None}
                    else:
                        result = {**query, "query_optimization": query["optimization"],
                                  "gallery_optimization": gallery_optimization, "scores": {},
                                  "exact_binary_match": query["artifact_sha256"] == own["artifact_sha256"],
                                  "correspondence": {
                                      key: fact_cache[query["artifact_sha256"]][key] ==
                                      gallery_facts[own["artifact_sha256"]][key]
                                      for key in ("selected_features", "tensors")}}
                        for method in METHODS:
                            result["scores"][method] = _rank(
                                values[method], gallery_vectors[gallery_optimization][method], origin,
                                lineage_ids[query["owner"]["split_group"]])
                    atomic_json(result_path, result, compact=True)
                    rows.append(result)
            controls = {}
            for row in rows:
                if any(recipe["family"] == "unchanged" for recipe in row["recipes"]):
                    controls[(row["origin_gallery_id"], row["query_optimization"],
                              row["gallery_optimization"])] = row
            for row in rows:
                control = controls.get((row["origin_gallery_id"], row["query_optimization"],
                                        row["gallery_optimization"]))
                for method, metric in row["scores"].items():
                    baseline = {} if control is None else control["scores"][method]
                    metric["change_from_unchanged"] = (
                        None if metric.get("original_score") is None or baseline.get("original_score") is None
                        else metric["original_score"] - baseline["original_score"])
            report = summarize(rows, scoped_queries, exclusions, scope, coverage)
            atomic_json(output / f"evaluation-{scope}.json",
                        {"format": FORMAT, "rows": rows, "summary": report}, compact=True)
            (output / f"report-{scope}.md").write_text(render_report(report))
            marker = {"status": "complete", "scope": scope, "queries": len(scoped_queries),
                      "observations": len(rows), "report": str(output / f"report-{scope}.md")}
            atomic_json(output / f"{scope.upper()}-COMPLETE.json", marker)
            if scope == "pilot":
                families = {recipe["family"] for query in scoped_queries for recipe in query["recipes"]}
                cells = {(row["query_optimization"], row["gallery_optimization"]) for row in rows}
                controls_ok = all(row["correspondence"] and
                                  row["correspondence"]["selected_features"] and
                                  row["correspondence"]["tensors"]
                                  for row in rows
                                  if row["query_optimization"] == row["gallery_optimization"] and
                                  any(recipe["family"] in {"unchanged", "formatting"} and
                                      recipe["status"] in {"applied", "unchanged"}
                                      for recipe in row["recipes"]))
                gates = {"all_families": {"unchanged", "formatting", "rename", "literal", "operator",
                                           "structural", "partial", "combined"} <= families,
                         "all_optimization_cells": len(cells) == 9,
                         "all_methods": all(set(row["scores"]) == set(METHODS) for row in rows),
                         "control_invariance": controls_ok,
                         "cardinality": gallery_counts == Counter({o: EXPECTED_GALLERY for o in OPTIMIZATIONS}) and
                                        query_counts == Counter(EXPECTED_QUERIES),
                         "model_scores_not_gate": True}
                atomic_json(output / "pilot-gates.json", {"pass": all(gates.values()), "gates": gates})
                if not all(gates.values()):
                    return {"status": "stopped", "scope": "pilot", "gates": gates}
            all_rows = rows
        result = {"status": "complete", "scope": "full", "queries": len(queries),
                  "observations": len(all_rows), "report": str(output / "report-full.md")}
        atomic_json(complete_path, result)
        partial = output / "PARTIAL.json"
        if partial.exists():
            partial.unlink()
        return result
    except BudgetExceeded as exc:
        result = {"status": "partial", "reason": str(exc),
                  "resume": _resume_command(input_run, output, checkpoints, max_seconds)}
        atomic_json(output / "PARTIAL.json", result)
        return result
