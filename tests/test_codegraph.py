import py_compile
import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from codegraph.backlog import DecompilerGap, append_gap
from codegraph.corpus_builder import _checkout, _included, build_corpus
from codegraph.ingest import ingest_path, ingest_source
from codegraph.manifest import load_manifest
from codegraph.fixtures import extract_fixture
from codegraph.curation import curated_inputs, stratified_splits
from codegraph.manifest import CorpusProject
from codegraph.sandbox import SandboxUnavailable
from codegraph.corpus import EmbeddingRecord, LocalFaissIndex
from codegraph.shared_model import (ProjectEmbeddingPool, SharedGraphEncoder,
                                    contrastive_loss, graph_tensors, hybrid_project_similarity)
from codegraph.synthetic import renamed_view
from codegraph.workflow import _batches
from codegraph.workflow import index_corpus, search_artifact, train_corpus
from codegraph.training import TrainingView


SOURCE = """
def add(value, other=1):
    result = value + other
    return result
"""


class CodeGraphTest(unittest.TestCase):
    def test_valid_source_produces_function_graph_and_embedding(self):
        result = ingest_source(SOURCE, origin="sample.py")
        self.assertEqual(result.lane, "ast")
        self.assertEqual(result.graphs[0].metadata["parse_status"], "valid")
        self.assertTrue(any(edge.kind == "def_use" for graph in result.graphs for edge in graph.edges))
        vector = SharedGraphEncoder(dimension=32, layers=2).encode_graph(result.graphs[0])
        self.assertEqual(vector.shape, (32,))

    def test_invalid_source_remains_comparable_recovery_graph(self):
        result = ingest_source("def broken(:\n", origin="broken.py", reconstructed=True)
        self.assertEqual(result.lane, "recovery")
        self.assertTrue(result.graphs[0].metadata["reconstructed"])
        self.assertEqual(result.graphs[0].metadata["parse_status"], "recovered")

    def test_current_runtime_pyc_is_decoded_in_worker(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "sample.py"
            source.write_text(SOURCE)
            compiled = Path(directory) / "sample.pyc"
            py_compile.compile(str(source), cfile=str(compiled), doraise=True)
            result = ingest_path(compiled, trusted=True)
        self.assertEqual(result.lane, "bytecode")
        self.assertTrue(any(node.kind == "core:operation" for node in result.graphs[0].nodes))

    def test_contrastive_loss_is_finite(self):
        import torch
        vectors = torch.nn.functional.normalize(torch.randn(4, 16), dim=-1)
        self.assertTrue(torch.isfinite(contrastive_loss(vectors, [(0, 1), (2, 3)])))

    def test_project_pool_and_local_search(self):
        import tempfile
        import torch
        vectors = torch.nn.functional.normalize(torch.randn(3, 16), dim=-1)
        project = ProjectEmbeddingPool(16)(vectors)
        self.assertTrue(torch.isfinite(hybrid_project_similarity(project, project, vectors, vectors)))
        with tempfile.TemporaryDirectory() as directory:
            index = LocalFaissIndex(directory, 16)
            index.upsert([EmbeddingRecord("one", vectors[0].tolist(), {"lane": "ast"}),
                          EmbeddingRecord("two", vectors[1].tolist(), {"lane": "bytecode"})])
            self.assertEqual(index.search(vectors[0].tolist(), limit=1)[0].id, "one")

    def test_untrusted_pyc_fails_closed_without_docker(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.pyc"
            path.write_bytes(b"\0" * 16)
            with patch("codegraph.ingest.run_isolated", side_effect=SandboxUnavailable("unavailable")):
                with self.assertRaises(SandboxUnavailable):
                    ingest_path(path)

    def test_manifest_and_backlog_are_validated_and_deduplicated(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "manifest.jsonl"
            manifest.write_text(json.dumps({"name": "example", "url": "https://example.test/repo.git",
                                             "revision": "a" * 40, "license": "MIT"}) + "\n")
            self.assertEqual(load_manifest(manifest)[0].name, "example")
            gap = DecompilerGap("3.12", "uncompyle6", "Unsupported", "sample", "message")
            self.assertTrue(append_gap(root / "gaps.jsonl", gap))
            self.assertFalse(append_gap(root / "gaps.jsonl", gap))

    def test_split_group_prevents_duplicate_repository_leakage(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "manifest.jsonl"
            manifest.write_text("\n".join([
                json.dumps({"name": "tool_source", "url": "https://example.test/tool.git",
                            "revision": "a" * 40, "license": "MIT", "corpus_role": "production",
                            "split_group": "tool"}),
                json.dumps({"name": "tool_fixtures", "url": "https://example.test/tool.git",
                            "revision": "a" * 40, "license": "MIT", "corpus_role": "fixture",
                            "split_group": "tool"}),
            ]) + "\n")
            records = load_manifest(manifest)
            from codegraph.corpus_builder import _split
            self.assertEqual(_split(records[0].split_group), _split(records[1].split_group))

    def test_manifest_rejects_conflicting_explicit_group_partitions(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "manifest.jsonl"
            manifest.write_text("\n".join([
                json.dumps({"name": "one", "url": "https://example.test/one.git", "revision": "a" * 40,
                            "license": "MIT", "split_group": "shared", "partition": "train"}),
                json.dumps({"name": "two", "url": "https://example.test/two.git", "revision": "a" * 40,
                            "license": "MIT", "split_group": "shared", "partition": "test"}),
            ]) + "\n")
            with self.assertRaises(ValueError):
                load_manifest(manifest)

    def test_synthetic_fixture_manifest_has_ten_versioned_projects(self):
        fixture_manifest = Path(__file__).parents[1] / "fixtures" / "synthetic" / "manifest.jsonl"
        fixtures = [json.loads(line) for line in fixture_manifest.read_text().splitlines()]
        self.assertEqual(len(fixtures), 10)
        for fixture in fixtures:
            source = fixture_manifest.parent / fixture["name"] / "main.py"
            self.assertTrue(source.exists())

    def test_local_manifest_builds_labeled_views_without_running_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = root / "repository"
            repository.mkdir()
            (repository / "sample.py").write_text(SOURCE)
            # A local git source exercises the same pinned-revision clone path as
            # a remote curated project without requiring network access.
            import subprocess
            subprocess.run(["git", "init", "-q", str(repository)], check=True)
            subprocess.run(["git", "-C", str(repository), "config", "user.email", "test@example.test"], check=True)
            subprocess.run(["git", "-C", str(repository), "config", "user.name", "Test"], check=True)
            subprocess.run(["git", "-C", str(repository), "add", "sample.py"], check=True)
            subprocess.run(["git", "-C", str(repository), "commit", "-qm", "fixture"], check=True)
            revision = subprocess.check_output(["git", "-C", str(repository), "rev-parse", "HEAD"], text=True).strip()
            manifest = root / "manifest.jsonl"
            manifest.write_text(json.dumps({"name": "local", "url": str(repository), "revision": revision,
                                             "license": "MIT"}) + "\n")
            result = build_corpus(manifest, root / "artifacts", max_units_per_project=1)
            self.assertEqual(result["projects"], 1)
            self.assertGreaterEqual(result["views"], 4)
            views = [json.loads(line) for line in (root / "artifacts" / "views.jsonl").read_text().splitlines()]
            self.assertEqual(len({view["artifact_id"] for view in views}), 1)
            self.assertTrue((root / "artifacts" / "graphs-manifest.jsonl").exists())
            self.assertTrue((root / "artifacts" / "COMPLETE.json").exists())

    def test_builder_preserves_old_syntax_without_modern_ast_transforms(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = root / "repository"
            repository.mkdir()
            (repository / "legacy.py").write_text("print 'legacy'\n")
            import subprocess
            subprocess.run(["git", "init", "-q", str(repository)], check=True)
            subprocess.run(["git", "-C", str(repository), "config", "user.email", "test@example.test"], check=True)
            subprocess.run(["git", "-C", str(repository), "config", "user.name", "Test"], check=True)
            subprocess.run(["git", "-C", str(repository), "add", "legacy.py"], check=True)
            subprocess.run(["git", "-C", str(repository), "commit", "-qm", "legacy"], check=True)
            revision = subprocess.check_output(["git", "-C", str(repository), "rev-parse", "HEAD"], text=True).strip()
            manifest = root / "manifest.jsonl"
            manifest.write_text(json.dumps({"name": "legacy", "url": str(repository), "revision": revision,
                                             "license": "MIT"}) + "\n")
            build_corpus(manifest, root / "artifacts")
            views = [json.loads(line) for line in (root / "artifacts" / "views.jsonl").read_text().splitlines()]
            self.assertIn("untransformed", {view["view_kind"] for view in views})

    def test_builder_labels_stub_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = root / "repository"
            repository.mkdir()
            (repository / "api.pyi").write_text("def parse(value: str) -> int: ...\n")
            import subprocess
            subprocess.run(["git", "init", "-q", str(repository)], check=True)
            subprocess.run(["git", "-C", str(repository), "config", "user.email", "test@example.test"], check=True)
            subprocess.run(["git", "-C", str(repository), "config", "user.name", "Test"], check=True)
            subprocess.run(["git", "-C", str(repository), "add", "api.pyi"], check=True)
            subprocess.run(["git", "-C", str(repository), "commit", "-qm", "stub"], check=True)
            revision = subprocess.check_output(["git", "-C", str(repository), "rev-parse", "HEAD"], text=True).strip()
            manifest = root / "manifest.jsonl"
            manifest.write_text(json.dumps({"name": "stub", "url": str(repository), "revision": revision,
                                             "license": "MIT", "source_extensions": [".pyi"],
                                             "include": ["**/*.pyi"]}) + "\n")
            build_corpus(manifest, root / "artifacts")
            view = json.loads((root / "artifacts" / "views.jsonl").read_text().splitlines()[0])
            self.assertEqual(view["metadata"]["source_kind"], ".pyi")

    def test_fixture_extractors_preserve_individual_cases_and_labels(self):
        mypy = extract_fixture("mypy", "[case bad]\ndef f(x: Missing) -> None: ...  # E: error\n[out]\nmsg\n")
        self.assertEqual(mypy[0].identifier, "bad")
        self.assertEqual(mypy[0].metadata["expected_outcome"], "diagnostic")
        markdown = extract_fixture("markdown", "# Rule\n```python\nx = 1  # error\n```\n")
        self.assertEqual(markdown[0].source, "x = 1  # error")
        black = extract_fixture("black", "x=1\n# output\nx = 1\n")
        self.assertEqual([entry.metadata["pair_role"] for entry in black], ["input", "output"])
        cpython = extract_fixture("cpython", 'check_syntax_error("def broken(:\\n")\n')
        self.assertEqual(cpython[0].metadata["parse_expectation"], "invalid")

    def test_curation_caps_inputs_deduplicates_across_projects_and_keeps_groups_together(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first, second = root / "first", root / "second"
            first.mkdir()
            second.mkdir()
            (first / "one.py").write_text("def shared():\n    return 1\n")
            (first / "two.py").write_text("def unique_one():\n    return 2\n")
            (second / "one.py").write_text("def shared():\n    return 1\n")
            (second / "two.py").write_text("def unique_two():\n    return 3\n")
            import subprocess
            for repository in (first, second):
                subprocess.run(["git", "init", "-q", str(repository)], check=True)
                subprocess.run(["git", "-C", str(repository), "config", "user.email", "test@example.test"], check=True)
                subprocess.run(["git", "-C", str(repository), "config", "user.name", "Test"], check=True)
                subprocess.run(["git", "-C", str(repository), "add", "."], check=True)
                subprocess.run(["git", "-C", str(repository), "commit", "-qm", "fixtures"], check=True)
            projects = [
                CorpusProject("first", "https://example.test/first.git", "a" * 40, "MIT", partition="auto"),
                CorpusProject("second", "https://example.test/second.git", "b" * 40, "MIT", split_group="shared"),
            ]
            inputs, report = curated_inputs(projects, root, cap=1)
            self.assertEqual(len(inputs), 2)
            self.assertEqual(report.excluded["cross_project_duplicate"], 1)
            self.assertEqual(report.excluded["repository_cap"], 1)
            splits = stratified_splits(projects)
            self.assertEqual(splits["shared"], inputs[1].split)

    def test_ast_ids_are_unique_and_schema_one_is_rejected(self):
        result = ingest_source("def f(a):\n    return -a + 1\n", origin="ids.py")
        for graph in result.graphs:
            identifiers = [node.id for node in graph.nodes]
            self.assertEqual(len(identifiers), len(set(identifiers)))
            graph.validate()
        value = result.graphs[0].to_dict()
        value["schema_version"] = 1
        from codegraph.semantic import ProgramGraph
        with self.assertRaises(ValueError):
            ProgramGraph.from_dict(value)

    def test_operator_values_affect_encoder_inputs_and_embeddings(self):
        plus = ingest_source("result = left + right\n", origin="plus.py").graphs[0]
        minus = ingest_source("result = left - right\n", origin="minus.py").graphs[0]
        left = graph_tensors(plus, node_buckets=2048, relation_buckets=512)["feature_ids"]
        right = graph_tensors(minus, node_buckets=2048, relation_buckets=512)["feature_ids"]
        self.assertFalse(__import__("torch").equal(left, right))
        model = SharedGraphEncoder(dimension=32, layers=1)
        vectors = model(graph for graph in [plus, minus]).detach()
        self.assertLess(float(vectors[0] @ vectors[1]), 0.999999)

    def test_renaming_preserves_parameters_and_runtime_behavior(self):
        source = "def total(value):\n    result = value + 2\n    return result\n"
        renamed = renamed_view(source, seed_material="stable")
        self.assertIn("def total(value)", renamed)
        self.assertIn("local_0 = value + 2", renamed)
        before: dict = {}
        after: dict = {}
        exec(source, before)
        exec(renamed, after)
        self.assertEqual(before["total"](3), after["total"](3))

    def test_loss_excludes_self_and_batches_never_truncate_positive_group(self):
        import torch
        identical = torch.tensor([[1.0, 0.0], [1.0, 0.0]])
        self.assertAlmostEqual(float(contrastive_loss(identical, [(0, 1)])), 0.0, places=6)
        graph = ingest_source("x = 1\n", origin="batch.py").graphs[0]
        views = [TrainingView(graph, "same", f"view-{index}") for index in range(6)]
        batches = list(_batches(views, size=4, seed=0))
        self.assertEqual([len(batch) for batch in batches], [6])

    def test_globstar_matches_package_root_and_nested_modules(self):
        project = CorpusProject("requests", "https://example.test/requests.git", "a" * 40,
                                "MIT", include=("src/requests/**/*.py",))
        self.assertTrue(_included(project, "src/requests/api.py"))
        self.assertTrue(_included(project, "src/requests/packages/urllib3.py"))

    def test_index_fingerprints_and_scores_are_enforced(self):
        with tempfile.TemporaryDirectory() as directory:
            index = LocalFaissIndex(directory, 2, fingerprint="model-a")
            index.upsert([EmbeddingRecord("one", [1.0, 0.0], {})])
            self.assertAlmostEqual(index.search_scored([1.0, 0.0])[0].score, 1.0)
            with self.assertRaises(ValueError):
                LocalFaissIndex(directory, 2, fingerprint="model-b")

    def test_checkout_conflict_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            conflict = root / "project"
            conflict.mkdir()
            sentinel = conflict / "owned-by-user.txt"
            sentinel.write_text("preserve me")
            project = CorpusProject("project", "https://example.test/project.git", "a" * 40, "MIT")
            with self.assertRaises(RuntimeError):
                _checkout(project, root)
            self.assertEqual(sentinel.read_text(), "preserve me")

    def test_schema_two_build_train_index_and_exact_search(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = root / "repository"
            repository.mkdir()
            query = repository / "sample.py"
            query.write_text(SOURCE)
            import subprocess
            subprocess.run(["git", "init", "-q", str(repository)], check=True)
            subprocess.run(["git", "-C", str(repository), "config", "user.email", "test@example.test"], check=True)
            subprocess.run(["git", "-C", str(repository), "config", "user.name", "Test"], check=True)
            subprocess.run(["git", "-C", str(repository), "add", "sample.py"], check=True)
            subprocess.run(["git", "-C", str(repository), "commit", "-qm", "fixture"], check=True)
            revision = subprocess.check_output(
                ["git", "-C", str(repository), "rev-parse", "HEAD"], text=True).strip()
            manifest = root / "manifest.jsonl"
            manifest.write_text(json.dumps({"name": "local", "url": str(repository),
                                             "revision": revision, "license": "MIT",
                                             "partition": "train"}) + "\n")
            corpus = root / "corpus"
            build_corpus(manifest, corpus)
            checkpoint = root / "model.pt"
            train_corpus(corpus, checkpoint, epochs=1, batch_size=16, seed=7)
            index_corpus(corpus, checkpoint, root / "index")
            result = search_artifact(query, checkpoint, root / "index")
            self.assertEqual(result["status"], "matched")
            self.assertEqual(result["confidence"], "exact")
            self.assertGreaterEqual(len(result["candidates"]), 1)
