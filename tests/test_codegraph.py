import py_compile
import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from codegraph.backlog import DecompilerGap, append_gap
from codegraph.corpus_builder import build_corpus
from codegraph.ingest import ingest_path, ingest_source
from codegraph.manifest import load_manifest
from codegraph.sandbox import SandboxUnavailable
from codegraph.corpus import EmbeddingRecord, LocalFaissIndex
from codegraph.shared_model import (ProjectEmbeddingPool, SharedGraphEncoder,
                                    contrastive_loss, hybrid_project_similarity)


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
        self.assertTrue(any(edge.kind == "def_use" for edge in result.graphs[0].edges))
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
            result = build_corpus(manifest, root / "artifacts")
            self.assertEqual(result["projects"], 1)
            self.assertGreaterEqual(result["views"], 4)

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
