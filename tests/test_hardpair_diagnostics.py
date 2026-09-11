import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import torch

from codegraph.hardpair_diagnostics import (
    ROOT, cosine, diagnose, facts, load_manifest, sparse_features, trace, verify_owned, verify_lock,
)
from codegraph.ingest import ingest_source
from codegraph.shared_model import SharedGraphEncoder


class HardpairDiagnosticsTest(unittest.TestCase):
    def test_family_splits_and_owned_development_oracles(self):
        rows = load_manifest()["families"]
        self.assertEqual(len(verify_lock()), 64)
        self.assertEqual({s: sum(r["split"] == s for r in rows)
                          for s in ("train", "validation", "test")},
                         {"train": 8, "validation": 3, "test": 3})
        for row in rows:
            with self.subTest(family=row["family"]):
                if row["split"] == "test":
                    with self.assertRaisesRegex(ValueError, "reserved test"):
                        verify_owned(row)
                    continue
                checks = verify_owned(row)
                self.assertTrue(all(checks["original"]))
                self.assertTrue(all(checks["positive"]))
                self.assertFalse(all(checks["negative"]))

    def test_test_scoring_is_rejected_before_checkpoint_load(self):
        with self.assertRaisesRegex(ValueError, "test is reserved"):
            diagnose("missing.pt", "unused", split="test")

    def test_diagnostic_gallery_report_and_immutable_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            checkpoint = root / "identity.pt"
            checkpoint.write_bytes(b"test checkpoint identity")
            model = SharedGraphEncoder(dimension=8, layers=2).eval()
            with patch("codegraph.hardpair_diagnostics._load_model", return_value=model):
                result = diagnose(checkpoint, root / "run")
            self.assertFalse(result["test_scored"])
            report = json.loads((root / "run" / "diagnostics.json").read_text())
            self.assertEqual(len(report["diagnostics"]), 8)
            self.assertEqual(len(report["retrieval"]), 40)
            self.assertEqual(len(report["pairs"]), 24)
            allowed = {r["family"] for r in load_manifest()["families"] if r["split"] == "train"}
            for row in report["retrieval"]:
                self.assertEqual(len(row["candidates"]), 9)
                self.assertTrue(all(c["family"] in allowed for c in row["candidates"]))
            for family in allowed:
                galleries = [{(c["family"], c["variant"]) for c in r["candidates"]}
                             for r in report["retrieval"] if r["family"] == family]
                self.assertTrue(all(g == galleries[0] for g in galleries))
            with self.assertRaisesRegex(ValueError, "new diagnostic output"):
                diagnose(checkpoint, root / "run")

    def test_schema_three_repairs_previous_information_loss(self):
        model = SharedGraphEncoder(dimension=8, layers=1)
        for name, loss in (("literal_limit", "graph"), ("extremum", "selected_features")):
            row = next(r for r in load_manifest()["families"] if r["family"] == name)
            variants = {}
            for kind in ("original", "negative"):
                graphs = ingest_source((ROOT / row["variants"][kind]).read_text()).graphs
                variants[kind] = {g.metadata["qualified_name"]: facts(g, model) for g in graphs}
            self.assertNotEqual(variants["original"]["run"][loss], variants["negative"]["run"][loss])
            self.assertNotEqual(variants["original"]["run"]["tensors"], variants["negative"]["run"]["tensors"])
            if name == "extremum":
                self.assertNotEqual(variants["original"]["run"]["graph"], variants["negative"]["run"]["graph"])

    def test_trace_matches_actual_encoder_without_leaking_hooks(self):
        model = SharedGraphEncoder(dimension=8, layers=2).eval()
        graph = ingest_source("def run(x):\n    return x + 1\n").graphs[-1]
        with torch.no_grad():
            expected = model.encode_graph(graph)
            actual, stages = trace(graph, model)
        self.assertTrue(torch.equal(expected, actual))
        self.assertEqual(set(stages), {"layer_0", "layer_1", "node_mean", "unit_vector"})
        self.assertFalse(model.project._forward_pre_hooks)
        self.assertTrue(all(not layer._forward_hooks for layer in model.layers))

    def test_operation_baseline_preserves_literal_and_api_changes(self):
        for a, b in (("return min(x)", "return max(x)"), ("return x >= 40", "return x >= 41")):
            left = sparse_features("def run(x):\n    " + a, "operation_api")
            right = sparse_features("def run(x):\n    " + b, "operation_api")
            self.assertLess(cosine(left, right), 1.0)

    def test_cross_family_duplicate_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            # Fixture setup is test code, not a workspace-edit mechanism.
            (root / "a.py").write_text("def run(x): return x\n")
            (root / "b.py").write_text("def run(x): return x\n")
            rows = [{"family": n, "split": s, "variants": {"original": n+".py"},
                     "oracle": n+".json"} for n,s in (("a","train"),("b","test"))]
            (root / "manifest.json").write_text(json.dumps({"families": rows}))
            with self.assertRaisesRegex(ValueError, "cross-family"):
                load_manifest(root)
