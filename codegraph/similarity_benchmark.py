"""Reproducible three-representation experiment over owned Python fixtures."""
from __future__ import annotations

import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import uuid

from .fixture_obfuscation import negative_control, obfuscate

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "similarity"
WORKER = Path(__file__).with_name("_similarity_worker.py")
RUNTIMES = {
    "3.4": "python:3.4.10-slim@sha256:44b78f9c6c93df7d8bc0d32a85ef8fd10a074a101985bde6fd41d3b5aadf16f0",
    "3.8": "python:3.8.20-slim@sha256:1d52838af602b4b5a831beb13a0e4d073280665ea7be7f69ce2382f29c5a613f",
    "3.12": "python:3.12-slim@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea",
    "3.14": "python:3.14-slim@sha256:cad9a2c871761c413caa6fdd6441c783451e740a48aaeba60ae62a8b53525ef6",
}
TOOLS_IMAGE = "pycmp-similarity-tools:v1"
FORMAT = 1


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def isolated(image: str, directory: Path, command: list[str], *, timeout: int = 30,
             platform: str | None = None) -> dict:
    name = "pycmp-similarity-" + uuid.uuid4().hex
    args = ["docker", "run", "--name", name, "--rm", "--network", "none",
            "--read-only", "--user", "65534:65534", "--pids-limit", "64",
            "--memory", "512m", "--cpus", "1", "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges", "--tmpfs", "/tmp:rw,size=64m",
            "-e", "PYTHONDONTWRITEBYTECODE=1", "-e", "PYTHONHASHSEED=0",
            "-v", str(directory.resolve()) + ":/input:ro",
            "-v", str(WORKER.resolve()) + ":/worker.py:ro"]
    if platform:
        args += ["--platform", platform]
    args += [image, *command]
    try:
        # Spool output and poll both size and time to keep parent memory bounded.
        # Kill the container too: killing only its Docker client is insufficient.
        with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
            process = subprocess.Popen(args, stdout=stdout, stderr=stderr)
            deadline = time.monotonic() + timeout
            status = None
            while process.poll() is None:
                if time.monotonic() >= deadline:
                    status = "timeout"
                elif max(os.fstat(stdout.fileno()).st_size, os.fstat(stderr.fileno()).st_size) > 1024 * 1024:
                    status = "output_limit"
                if status:
                    process.kill()
                    process.wait()
                    break
                time.sleep(0.05)
            code = process.returncode
            status = status or ("ok" if code == 0 else "failed")
            stdout.seek(0)
            stderr.seek(0)
            out, err = stdout.read(1024 * 1024), stderr.read(1024 * 1024)
        return {"status": status, "returncode": code,
                "stdout": out.decode(errors="replace"), "stderr": err.decode(errors="replace")}
    finally:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=15)


def runtime_call(version: str, directory: Path, mode: str, optimization: int = 0) -> dict:
    flags = [] if optimization == 0 else ["-" + "O" * optimization]
    result = isolated(RUNTIMES[version], directory,
                      ["python", *flags, "/worker.py", mode, str(optimization)],
                      platform="linux/amd64" if version in {"3.4", "3.8"} else None)
    if result["status"] == "ok":
        try:
            result["response"] = json.loads(result["stdout"])
        except json.JSONDecodeError:
            result["status"] = "invalid_output"
    return result


def stage(directory: Path, modules: dict[str, str], oracle: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for name, source in modules.items():
        (directory / name).write_text(source)
    shutil.copyfile(oracle, directory / "oracle.json")


def accepted(result: dict) -> bool:
    return result.get("status") == "ok" and result.get("response", {}).get("passed") is True


def classify_reconstruction(tool_result: dict, verification: dict | None) -> str:
    if tool_result["status"] == "timeout":
        return "timeout"
    if tool_result["status"] == "output_limit":
        return "invalid_output"
    if not any(line.strip() and not line.lstrip().startswith("#")
               for line in tool_result.get("stdout", "").splitlines()):
        message = tool_result.get("stderr", "").lower()
        return "unsupported" if "unsupported" in message else "invalid_output"
    if verification and accepted(verification) and tool_result["returncode"] == 0:
        diagnostics = tool_result.get("stderr", "").lower() + tool_result["stdout"].lower()
        if "unsupported opcode" not in diagnostics and "incomplete" not in diagnostics:
            return "success"
    message = (tool_result.get("stdout", "") + tool_result.get("stderr", "")).lower()
    if "unsupported" in message:
        return "unsupported"
    if verification:
        if verification.get("response") is not None:
            return "behavior_mismatch"
        if "syntaxerror" in verification.get("stderr", "").lower():
            return "invalid_output"
    return "partial" if tool_result.get("stdout", "").strip() else "invalid_output"


def build(output: str | Path, *, workers: int = 4) -> dict:
    if not 1 <= workers <= 8:
        raise ValueError("workers must be between 1 and 8")
    output = Path(output).resolve()
    if (output / "COMPLETE.json").exists():
        raise ValueError("completed run is immutable; choose a new output directory")
    output.mkdir(parents=True, exist_ok=True)
    fixtures = json.loads((FIXTURES / "manifest.json").read_text())
    # Resolve the tools tag to an immutable image ID before the first task.
    info = subprocess.run(["docker", "image", "inspect", TOOLS_IMAGE],
                          capture_output=True, text=True, check=True, timeout=30)
    tools = json.loads(info.stdout)[0]
    tools_id = tools["Id"]
    record = {"format": FORMAT, "fixtures": fixtures, "runtimes": RUNTIMES,
              "tools_image": tools_id, "tools_labels": tools["Config"].get("Labels"),
              "uncompyle6": "3.9.3", "xdis": "6.1.8", "seeds": [0, 1, 2],
              "generator_hash": digest(Path(__file__)),
              "worker_hash": digest(WORKER), "obfuscator_hash": digest(
                  Path(__file__).with_name("fixture_obfuscation.py"))}
    write_json(output / "definition.json", record)
    probe_results = []
    probe_source = 'def run(payload):\n    """optimization sentinel"""\n    assert payload["value"] >= 0\n    return [__debug__, run.__doc__]\n'
    # Compiler optimizations intentionally change assertions/docstrings.
    # Verify these semantics separately from the behavior-preserving fixtures.
    for version in RUNTIMES:
        for optimization in range(3):
            probe = output / "optimization-probes" / version / str(optimization)
            expected = [optimization == 0, "optimization sentinel" if optimization < 2 else None]
            cases = [{"input": {"value": 1}, "expected": expected},
                     {"input": {"value": -1}, **({"error": "AssertionError"} if optimization == 0
                                               else {"expected": expected})}]
            write_json(probe / "oracle.json", cases)
            (probe / "main.py").write_text(probe_source)
            compiled = runtime_call(version, probe, "compile", optimization)
            write_json(probe / "compile.json", compiled)
            bytecode = probe / "bytecode"
            bytecode.mkdir(exist_ok=True)
            shutil.copyfile(probe / "oracle.json", bytecode / "oracle.json")
            if compiled["status"] == "ok":
                for item in compiled["response"]["artifacts"]:
                    (bytecode / item["file"]).write_bytes(base64.b64decode(item["base64"]))
                checked = runtime_call(version, bytecode, "bytecode", optimization)
            else:
                checked = compiled
            write_json(probe / "verification.json", checked)
            probe_results.append({"runtime": version, "optimization": optimization, "passed": accepted(checked)})
    write_json(output / "optimization-probes.json", probe_results)
    if not all(row["passed"] for row in probe_results):
        raise RuntimeError("compiler optimization probes failed; inspect optimization-probes/")
    source_jobs = []
    bytecode_jobs = []
    variants = []
    for project in fixtures:
        name = project["name"]
        directory = FIXTURES / name
        modules = {file: (directory / file).read_text() for file in project["modules"]}
        oracle = directory / "oracle.json"
        original = output / name / "original"
        stage(original, modules, oracle)
        variants.append({"project": name, "kind": "original", "path": str(original.relative_to(output)),
                         "modules": project["modules"]})
        minimum = project["python_min"]
        for level in ("light", "structural"):
            for seed in (0, 1, 2):
                transformed, mapping = obfuscate(modules, level=level, seed=seed)
                target = output / name / ("obfuscated-" + level + "-" + str(seed))
                stage(target, transformed, oracle)
                write_json(target / "transformation.json", mapping)
                variants.append({"project": name, "kind": level, "seed": seed,
                                 "path": str(target.relative_to(output)), "modules": project["modules"]})
        negative = output / name / "negative"
        stage(negative, negative_control(modules), oracle)
        variants.append({"project": name, "kind": "negative", "path": str(negative.relative_to(output)),
                         "modules": project["modules"]})
        for version in RUNTIMES:
            if tuple(map(int, version.split("."))) < tuple(map(int, minimum.split("."))):
                continue
            for variant in variants:
                if variant["project"] == name:
                    source_jobs.append((variant, version))
            for optimization in range(3):
                bytecode_jobs.append((project, version, optimization))

    def source_job(job):
        variant, version = job
        result = runtime_call(version, output / variant["path"], "source")
        write_json(output / variant["path"] / ("oracle-" + version + ".json"), result)
        return {"path": variant["path"], "version": version, "passed": accepted(result)}

    def bytecode_job(job):
        project, version, optimization = job
        name = project["name"]
        root = output / name / ("python-" + version) / ("opt-" + str(optimization))
        root.mkdir(parents=True, exist_ok=True)
        compilation = runtime_call(version, output / name / "original", "compile", optimization)
        write_json(root / "compile.json", compilation)
        row = {"project": name, "runtime": version, "optimization": optimization,
               "compilation": compilation["status"], "tools": []}
        if compilation["status"] != "ok":
            return row
        bytecode = root / "bytecode"
        bytecode.mkdir(exist_ok=True)
        shutil.copyfile(FIXTURES / name / "oracle.json", bytecode / "oracle.json")
        artifacts = compilation["response"]["artifacts"]
        for item in artifacts:
            (bytecode / item["file"]).write_bytes(base64.b64decode(item["base64"]))
        compiled_oracle = runtime_call(version, bytecode, "bytecode", optimization)
        write_json(root / "bytecode-oracle.json", compiled_oracle)
        row["bytecode_passed"] = accepted(compiled_oracle)
        row["artifacts"] = [{"path": str((bytecode / item["file"]).relative_to(output)),
                             "sha256": digest(bytecode / item["file"]), "magic": item["magic"],
                             "module": item["module"]} for item in artifacts]
        for tool in ("uncompyle6", "pycdc"):
            reconstructed = root / tool
            reconstructed.mkdir(exist_ok=True)
            shutil.copyfile(FIXTURES / name / "oracle.json", reconstructed / "oracle.json")
            module_results = []
            for item in artifacts:
                command = [tool, "/input/" + item["file"]]
                result = isolated(tools_id, bytecode, command)
                # Keep only tool output. No original implementation is mounted.
                (reconstructed / item["module"]).write_text(result["stdout"])
                write_json(reconstructed / (item["module"] + ".tool.json"), result)
                module_results.append(result)
            verification = runtime_call(version, reconstructed, "source", optimization)
            write_json(reconstructed / "verification.json", verification)
            states = [classify_reconstruction(result, verification) for result in module_results]
            status = "success" if all(state == "success" for state in states) else next(
                state for state in states if state != "success")
            row["tools"].append({"tool": tool, "status": status, "modules": project["modules"],
                                 "behavior_passed": accepted(verification),
                                 "path": str(reconstructed.relative_to(output))})
        write_json(root / "result.json", row)
        return row

    source_results, results = [], []
    for jobs, function, destination, label in (
        (source_jobs, source_job, source_results, "source checks"),
        (bytecode_jobs, bytecode_job, results, "compile/decompile"),
    ):
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(function, job) for job in jobs]
            for number, future in enumerate(as_completed(futures), 1):
                destination.append(future.result())
                if number % 10 == 0 or number == len(futures):
                    print("%s: %s/%s" % (label, number, len(futures)), flush=True)
    for variant in variants:
        checks = [row for row in source_results if row["path"] == variant["path"]]
        variant["behavior_passed"] = bool(checks) and all(row["passed"] for row in checks)
    write_json(output / "variants.json", variants)
    write_json(output / "results.json", sorted(results, key=lambda row: (
        row["project"], row["runtime"], row["optimization"])))
    write_json(output / "source-checks.json", source_results)
    inventory = {path.relative_to(output).as_posix(): digest(path)
                 for path in sorted(output.rglob("*")) if path.is_file() and path.name != "COMPLETE.json"}
    write_json(output / "COMPLETE.json", {"format": FORMAT, "inventory": inventory})
    return {"combinations": len(results), "source_checks": len(source_results),
            "reconstructions": dict(Counter(tool["status"] for row in results for tool in row["tools"])),
            "output": str(output)}


def verify_inventory(root: Path) -> None:
    complete = json.loads((root / "COMPLETE.json").read_text())
    for relative, expected in complete["inventory"].items():
        path = root / relative
        if not path.is_file() or digest(path) != expected:
            raise ValueError("artifact checksum mismatch: " + relative)


def evaluate(root: str | Path, checkpoint: str | Path) -> dict:
    import ast
    import torch
    from .ingest import ingest_source
    from .shared_model import SharedGraphEncoder, graph_tensors
    from .training import TrainingView
    from .workflow import _hashed_graph_vectors, _load_model

    root = Path(root)
    verify_inventory(root)
    trained = _load_model(checkpoint)
    torch.manual_seed(0)
    untrained = SharedGraphEncoder(dimension=trained.dimension, layers=len(trained.layers),
                                   node_buckets=trained.node_buckets,
                                   relation_buckets=trained.relation_buckets).eval()
    variants = json.loads((root / "variants.json").read_text())
    results = json.loads((root / "results.json").read_text())
    for row in results:
        for tool in row["tools"]:
            variants.append({**tool, "project": row["project"], "kind": "decompiled",
                             "runtime": row["runtime"], "optimization": row["optimization"]})
    cache = {}
    evidence = {}
    for variant in variants:
        path = variant["path"]
        files, ast_hashes, raw_hashes, input_hashes = [], {}, {}, {}
        for module in variant["modules"]:
            source = (root / path / module).read_text()
            raw_hashes[module] = hashlib.sha256(source.encode()).hexdigest()
            if not source.strip() or not any(
                    line.strip() and not line.lstrip().startswith("#") for line in source.splitlines()):
                continue
            try:
                tree = ast.parse(source)
                ast_hashes[module] = hashlib.sha256(ast.dump(tree).encode()).hexdigest()
            except SyntaxError:
                ast_hashes[module] = None
            graphs = ingest_source(source, origin=module,
                                   reconstructed=variant["kind"] == "decompiled").graphs
            tensor_facts = []
            for graph in graphs:
                facts = graph_tensors(graph, node_buckets=trained.node_buckets,
                                      relation_buckets=trained.relation_buckets)
                tensor_facts.append({key: value.tolist() for key, value in facts.items()
                                     if key != "availability"})
            input_hashes[module] = hashlib.sha256(json.dumps(tensor_facts, sort_keys=True).encode()).hexdigest()
            files.append(graphs)
        evidence[path] = {"files": len(files), "expected_files": len(variant["modules"]),
                          "units": sum(map(len, files)), "raw_hashes": raw_hashes,
                          "ast_hashes": ast_hashes, "input_hashes": input_hashes}
        if not files:
            continue
        vectors = {}
        with torch.no_grad():
            for method, model in (("trained", trained), ("untrained", untrained), ("hashed_graph", None)):
                file_vectors = []
                for graphs in files:
                    unit_vectors = (model(graphs) if model else _hashed_graph_vectors([
                        TrainingView(graph, "", "") for graph in graphs]))
                    file_vectors.append(torch.nn.functional.normalize(unit_vectors.mean(0), dim=0))
                vectors[method] = torch.nn.functional.normalize(torch.stack(file_vectors).mean(0), dim=0)
        cache[path] = vectors
    originals = {v["project"]: v for v in variants if v["kind"] == "original"}
    negatives = {v["project"]: v for v in variants if v["kind"] == "negative"}
    comparisons = []

    def compare(left, right):
        a, b = left["path"], right["path"]
        row = {"project": left["project"], "left": a, "right": b,
               "left_kind": left["kind"], "right_kind": right["kind"],
               "right_status": right.get("status"), "runtime": right.get("runtime"),
               "optimization": right.get("optimization"), "tool": right.get("tool"),
               "seed": right.get("seed"), "behavior_passed": bool(
                   left.get("behavior_passed") and right.get("behavior_passed")),
               "coverage": {a: evidence[a], b: evidence[b]}}
        row["exact_match"] = evidence[a]["raw_hashes"] == evidence[b]["raw_hashes"]
        row["ast_match"] = (bool(evidence[a]["ast_hashes"]) and
                            None not in evidence[a]["ast_hashes"].values() and
                            evidence[a]["ast_hashes"] == evidence[b]["ast_hashes"])
        row["identical_model_inputs"] = (bool(evidence[a]["input_hashes"]) and
                                         evidence[a]["input_hashes"] == evidence[b]["input_hashes"])
        row["scores"] = {}
        if a in cache and b in cache:
            for method in cache[a]:
                cosine = max(-1.0, min(1.0, float(cache[a][method] @ cache[b][method])))
                row["scores"][method] = {"cosine": cosine, "percent": cosine * 100}
        comparisons.append(row)

    for variant in variants:
        if variant["kind"] != "original":
            compare(originals[variant["project"]], variant)
    for decompiled in (v for v in variants if v["kind"] == "decompiled"):
        for obfuscated in (v for v in variants if v["project"] == decompiled["project"]
                           and v["kind"] in {"light", "structural"}):
            compare(obfuscated, decompiled)
    retrieval = []
    for variant in variants:
        path = variant["path"]
        if path not in cache:
            continue
        for method in cache[path]:
            scored = sorted([(float(cache[path][method] @ cache[original["path"]][method]), name)
                             for name, original in originals.items()], reverse=True)
            own = next(score for score, name in scored if name == variant["project"])
            # Conservative ties: all other projects at least as close precede own.
            rank = 1 + sum(score >= own - 1e-7 for score, name in scored if name != variant["project"])
            negative_path = negatives[variant["project"]]["path"]
            negative_score = (float(cache[path][method] @ cache[negative_path][method])
                              if variant["kind"] != "negative" else None)
            retrieval.append({"path": path, "kind": variant["kind"], "method": method,
                              "project": variant["project"], "original_rank": rank,
                              "hard_negative_percent": None if negative_score is None else negative_score * 100,
                              "positive_margin": None if negative_score is None else own - negative_score,
                              "original_rank_with_hard_negative": None if negative_score is None else
                                  rank + int(negative_score >= own - 1e-7),
                              "candidates": [{"project": name, "percent": score * 100}
                                             for score, name in scored]})
    report = {"format": FORMAT, "checkpoint": str(checkpoint), "checkpoint_sha256": digest(Path(checkpoint)),
              "evaluation_code_sha256": digest(Path(__file__)),
              "definition_sha256": digest(root / "definition.json"),
              "similarity_definition": "100 * cosine; signed score, not probability",
              "reconstruction_statuses": dict(Counter(tool["status"] for row in results for tool in row["tools"])),
              "comparisons": comparisons, "retrieval": retrieval, "variants": variants}
    write_json(root / "evaluation.json", report)
    write_json(root / "embeddings.json", {path: {method: vector.tolist()
                                                for method, vector in vectors.items()}
                                          for path, vectors in cache.items()})
    markdown = render_report(report)
    (root / "report.md").write_text(markdown)
    return {"report": str(root / "report.md"), "comparisons": len(comparisons),
            "checkpoint_sha256": report["checkpoint_sha256"],
            "reconstruction_statuses": report["reconstruction_statuses"]}


def render_report(report: dict) -> str:
    from statistics import mean
    lines = ["# Synthetic project similarity experiment", "",
             "Scores are 100 × cosine similarity, not probabilities or equivalence percentages.",
             "The checkpoint was frozen; these projects were not used for training.", "",
             "Checkpoint SHA256: `" + report["checkpoint_sha256"] + "`.", "",
             "## Reconstruction coverage", "",
             "| Status | Project/runtime/optimization/tool attempts |", "|---|---:|"]
    lines += ["| %s | %s |" % item for item in sorted(report["reconstruction_statuses"].items())]
    lines += ["", "## Original versus variants", "",
              "Means below include only behavior-checked source variants and complete successful reconstructions.",
              "Negative controls are intentionally behavior-changing. Missing successful reconstructions are N/A.", "",
              "| Project | Decompiled % | Light % | Structural % | Negative % |",
              "|---|---:|---:|---:|---:|"]
    names = sorted({v["project"] for v in report["variants"]})
    for name in names:
        cells = []
        for kind in ("decompiled", "light", "structural", "negative"):
            rows = [r for r in report["comparisons"] if r["project"] == name
                    and r["left_kind"] == "original" and r["right_kind"] == kind
                    and r["scores"] and (kind == "negative" or r["behavior_passed"])
                    and (kind != "decompiled" or r["right_status"] == "success")]
            cells.append("%.2f" % mean(r["scores"]["trained"]["percent"] for r in rows) if rows else "N/A")
        lines.append("| " + name + " | " + " | ".join(cells) + " |")
    lines += ["", "## Pairwise detail", "",
              "Each row retains runtime, optimization, tool and obfuscation seed in its artifact paths.",
              "Scores for failed/partial reconstructions are diagnostic only. See JSON for file/unit coverage.",
              "", "| Project | Left | Right | Status | Behavior | GNN % | Untrained % | Graph % | Identical inputs |",
              "|---|---|---|---|---|---:|---:|---:|---|"]
    for row in report["comparisons"]:
        values = ["%.2f" % row["scores"][method]["percent"] if row["scores"] else "N/A"
                  for method in ("trained", "untrained", "hashed_graph")]
        lines.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            row["project"], row["left"], row["right"], row["right_status"] or "source",
            row["behavior_passed"], " | ".join(values), row["identical_model_inputs"]))
    lines += ["", "## Retrieval ranks against ten originals", "",
              "The extra hard-negative candidate is the query project's behavior-changing near-copy.", "",
              "| Variant | Method | Original rank (ties conservative) | Rank with hard negative |", "|---|---|---:|---:|"]
    for row in report["retrieval"]:
        lines.append("| %s | %s | %s | %s |" % (row["path"], row["method"], row["original_rank"],
                                                row["original_rank_with_hard_negative"] or "N/A"))
    return "\n".join(lines) + "\n"
