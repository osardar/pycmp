import ast
import tempfile
from pathlib import Path
import unittest

from codegraph.corpus_similarity import _prepare_definition, _rank, classify_decompiler
from codegraph.corpus_transforms import DOSES, FAMILIES, formatting, select_nested, transform, unchanged
from codegraph.bytecode_similarity import (_prepare_output as prepare_bytecode_output,
                                           build_manifests, opcode_structure)
from codegraph.semantic import GraphEdge, GraphNode, ProgramGraph


SOURCE = '''# retained comment
def outer(value: int):  # type evidence
    """retained docstring"""
    first = value + 10
    second = "text"
    if first < 20:
        result = first * 2
    else:
        result = first // 2
    def nested(item):
        local = item + first
        return local
    return nested(result), second

class Spare:
    pass
'''


class CorpusTransformsTest(unittest.TestCase):
    def test_nested_selection_is_deterministic_and_monotonic(self):
        eligible = [f"location-{number}" for number in range(20)]
        selected = [select_nested(eligible, dose, 1) for dose in DOSES]
        self.assertEqual(selected, [select_nested(eligible, dose, 1) for dose in DOSES])
        self.assertLessEqual(selected[0], selected[1])
        self.assertLessEqual(selected[1], selected[2])

    def test_every_family_applies_and_declares_parseable_edits(self):
        for family in FAMILIES:
            with self.subTest(family=family):
                result = transform(SOURCE, family, 0.6, 0)
                self.assertEqual(result.status, "applied", result.reason)
                self.assertGreater(result.actual_edit_count, 0)
                ast.parse(result.source, type_comments=True)

    def test_rename_preserves_comments_type_annotations_and_nested_binding(self):
        result = transform(SOURCE, "rename", 0.6, 2)
        self.assertEqual(result.status, "applied")
        self.assertIn("# retained comment", result.source)
        self.assertIn("value: int", result.source)
        self.assertIn('"""retained docstring"""', result.source)
        self.assertIn("related_2_", result.source)

    def test_literal_excludes_docstrings_and_handles_unicode_byte_spans(self):
        source = '# café\ndef f():\n    """café doc"""\n    value = "π"\n    return value + 3\n'
        result = transform(source, "literal", 0.6, 0)
        self.assertEqual(result.status, "applied")
        self.assertIn('"""café doc"""', result.source)
        self.assertIn("# café", result.source)
        ast.parse(result.source)

    def test_partial_retains_at_least_one_top_level_definition(self):
        result = transform(SOURCE, "partial", 0.6, 0)
        tree = ast.parse(result.source)
        definitions = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))]
        self.assertGreaterEqual(len(definitions), 1)

    def test_unsupported_and_controls_are_explicit(self):
        source = "def f(x):\n    return locals()[x]\n"
        renamed = transform(source, "rename", 0.6, 0)
        self.assertEqual(renamed.status, "unsupported")
        self.assertEqual(unchanged(source).status, "unchanged")
        self.assertIn(formatting(source).status, {"applied", "unchanged"})

    def test_rank_uses_conservative_ties_and_missing_origin(self):
        import torch
        query = torch.tensor([1.0, 0.0])
        ranked = _rank(query, [("own", query), ("tie", query)], "own")
        self.assertEqual(ranked["original_rank"], 2)
        self.assertEqual(_rank(query, [("other", query)], "own")["status"], "missing_origin")
        dense = _rank(query, (["own", "tie"], torch.stack([query, query])), "own")
        self.assertEqual(dense, ranked)

    def test_decompiler_failures_are_not_promoted(self):
        base = {"status": "ok", "returncode": 0, "stdout": "def f():\n    return 1\n", "stderr": ""}
        self.assertEqual(classify_decompiler(base)[0], "clean_parseable")
        self.assertEqual(classify_decompiler({**base, "stdout": "def broken("})[0], "partial_recovery")
        self.assertEqual(classify_decompiler({**base, "stdout": "", "stderr": "unsupported version"})[0],
                         "unsupported")
        self.assertEqual(classify_decompiler({**base, "status": "timeout"})[0], "timeout")

    def test_resume_requires_identical_definition(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _prepare_definition(root, {"version": 1}, False)
            _prepare_definition(root, {"version": 1}, True)
            with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
                _prepare_definition(root, {"version": 2}, True)

    def test_bytecode_manifests_keep_paired_origins_and_deduplicate_artifacts(self):
        provenance = [
            {"query_gallery_id": "origin-1", "variant_sha256": "source-1",
             "family": "unchanged", "status": "unchanged", "owner": {"repository": "r1",
             "split": "train", "split_group": "g1"}},
            {"query_gallery_id": "origin-1", "variant_sha256": "source-2",
             "family": "formatting", "status": "applied", "owner": {"repository": "r1",
             "split": "train", "split_group": "g1"}},
            {"query_gallery_id": "origin-2", "variant_sha256": "source-3",
             "family": "unchanged", "status": "unchanged", "owner": {"repository": "r2",
             "split": "validation", "split_group": "g2"}},
        ]
        compiled = []
        artifacts = set()
        for optimization in range(3):
            for source, artifact in (("source-1", f"original-{optimization}"),
                                     ("source-2", (f"formatted-{optimization}" if optimization == 0
                                                   else f"original-{optimization}"))):
                compiled.append({"source_sha256": source, "runtime": "3.14",
                                 "optimization": optimization, "status": "compiled",
                                 "artifact_sha256": artifact})
                artifacts.add(artifact)
        # The second origin lacks two gallery configurations and is excluded.
        compiled.append({"source_sha256": "source-3", "runtime": "3.14", "optimization": 0,
                         "status": "compiled", "artifact_sha256": "incomplete-origin"})
        artifacts.add("incomplete-origin")
        lanes = [{"artifact_sha256": artifact,
                  "decode": {"status": "decoded", "graph_path": f"decoded/{artifact}.json"}}
                 for artifact in artifacts]
        galleries, queries, exclusions = build_manifests(compiled, lanes, provenance)
        self.assertEqual(len(galleries), 3)
        self.assertEqual({row["origin_gallery_id"] for row in queries}, {"origin-1"})
        self.assertEqual({optimization: sum(row["optimization"] == optimization for row in queries)
                          for optimization in range(3)}, {0: 2, 1: 1, 2: 1})
        optimized = next(row for row in queries if row["optimization"] == 1)
        self.assertEqual({recipe["family"] for recipe in optimized["recipes"]},
                         {"unchanged", "formatting"})
        self.assertIn("missing_origin", {row["reason"] for row in exclusions})

    def test_opcode_structure_is_deterministic_and_uses_control_edges(self):
        graph = ProgramGraph(
            schema_version=3, unit_id="bytecode", unit_kind="function",
            nodes=[GraphNode("n0", "core:function", {"semantic_kind": "function"}, ("semantic_kind",)),
                   GraphNode("n1", "core:operation", {"opcode": "LOAD_CONST", "argument_kind": "int"},
                             ("opcode", "argument_kind")),
                   GraphNode("n2", "core:operation", {"opcode": "RETURN_VALUE", "argument_kind": "none"},
                             ("opcode", "argument_kind"))],
            edges=[GraphEdge("n0", "n1", "contains", ("bytecode",), {}),
                   GraphEdge("n1", "n2", "control_next", ("bytecode",), {})],
            metadata={"lane": "bytecode", "parse_status": "valid"})
        first = opcode_structure(graph)
        self.assertEqual(first, opcode_structure(graph))
        self.assertEqual(first["opcode:LOAD_CONST"], 1)
        self.assertEqual(first["edge:control_next:LOAD_CONST:RETURN_VALUE"], 1)

    def test_bytecode_resume_requires_an_identical_definition(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prepare_bytecode_output(root, {"version": 1, "counts": {0: 3}}, False)
            prepare_bytecode_output(root, {"version": 1, "counts": {0: 3}}, True)
            with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
                prepare_bytecode_output(root, {"version": 2}, True)


if __name__ == "__main__":
    unittest.main()
