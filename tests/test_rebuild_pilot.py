import tempfile
from pathlib import Path
import unittest

from codegraph.ingest import ingest_source
from codegraph.manifest import load_manifest
from codegraph.rebuild_pilot import run, transformation_findings
from codegraph.synthetic import renamed_view


class RebuildPilotTest(unittest.TestCase):
    def test_pilot_is_pinned_bounded_and_static(self):
        projects = load_manifest(Path(__file__).resolve().parents[1] / "corpus/schema3-pilot.jsonl")
        self.assertEqual(len(projects), 6)
        self.assertEqual(sum(len(p.include) for p in projects), 8)
        self.assertTrue(all(p.partition != "auto" and p.execution_policy == "static_only" for p in projects))
        self.assertTrue(all(not any('*' in path for path in p.include) for p in projects))

    def test_pilot_refuses_overwrite_before_build(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with self.assertRaisesRegex(ValueError, "new pilot directory"):
                run(root / "missing-manifest", root, root, root)

    def test_diagnostics_record_type_comment_loss(self):
        source = "x = 1  # type: int\n"
        transformed = renamed_view(source, seed_material="pilot")
        result = transformation_findings(source, transformed, ingest_source(source).graphs,
                                         ingest_source(transformed).graphs)
        self.assertEqual((result["type_facts_before"], result["type_facts_after"]), (1, 0))
        self.assertTrue(result["units"])
