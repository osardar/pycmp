import ast
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from codegraph.corpus_builder import build_corpus, GRAPH_PIPELINE_VERSION
from codegraph.curation import CuratedInput, canonical_hash, raw_hash
from codegraph.fixtures import FixtureInput
from codegraph.manifest import CorpusProject
from codegraph.synthetic import format_result, rename_result


class TransformRepairTest(unittest.TestCase):
    def preserves(self, source, expected):
        transformed = rename_result(source, seed_material="regression")
        self.assertEqual(transformed.status, "applied")
        before, after = {}, {}
        exec(compile(source, "owned-before.py", "exec"), before)
        exec(compile(transformed.source, "owned-after.py", "exec"), after)
        self.assertEqual(before["run"](), expected)
        self.assertEqual(after["run"](), expected)
        return transformed.source

    def test_nested_parameter_shadowing_counterexample(self):
        text = self.preserves("def run():\n    value=10\n    def inner(value):\n        return value+1\n    return inner(2)\n", 3)
        self.assertIn("return value+1", text)

    def test_lambda_closure_defaults_and_comprehension(self):
        cases = [
            ("def run():\n x=10\n fn=lambda x: x+1\n return fn(2)\n", 3),
            ("def run():\n x=10\n def inner(y=x): return x+y\n return inner(2)\n", 12),
            ("def run():\n x=10\n values=[x+1 for x in [1,2]]\n return [x, values]\n", [10,[2,3]]),
            ("def run():\n values=[1,2]\n result=[(last:=x+1) for x in values]\n return [last,result]\n", [3,[2,3]]),
        ]
        for source, expected in cases:
            with self.subTest(source=source):
                self.preserves(source, expected)

    def test_capture_names_and_global_nonlocal_are_not_rewritten(self):
        self.preserves("x=7\ndef run():\n global x\n value=2\n def inner():\n  nonlocal value\n  value+=1\n inner()\n answer=x+value\n return answer\n", 10)
        self.preserves("def run():\n try:\n  raise ValueError(3)\n except ValueError as error:\n  result=error.args[0]\n return result\n", 3)
        self.preserves("def run():\n value=[3]\n match value:\n  case [capture]:\n   answer=capture+1\n return answer\n", 4)

    def test_collision_free_names_unicode_and_fstrings(self):
        self.preserves("local_0=8\ndef run():\n café=3\n value=f'{café}:{local_0}'\n return value\n", "3:8")

    def test_typing_comments_literal_spelling_and_lines_preserved(self):
        source="def run():\n    value=0x10  # type: int\n    result=value+1  # type: ignore[assignment]\n    return result\n"
        out = self.preserves(source, 17)
        self.assertIn("0x10  # type: int", out)
        a, b = ast.parse(source, type_comments=True), ast.parse(out, type_comments=True)
        self.assertEqual([(n.lineno,n.tag) for n in a.type_ignores], [(n.lineno,n.tag) for n in b.type_ignores])
        self.assertEqual(source.count("\n"), out.count("\n"))
        annotated = "def run():\n Alias=int\n value=1  # type: Alias\n return value\n"
        transformed = rename_result(annotated, seed_material="annotations")
        self.assertIn("Alias=int", transformed.source)
        self.assertIn("# type: Alias", transformed.source)

    def test_dynamic_annotation_and_roundtrip_exclusions_are_explicit(self):
        for source in ("def run():\n x=1\n return eval('x')\n", "def run():\n x=1\n return locals()\n"):
            result = rename_result(source, seed_material="dynamic")
            self.assertEqual(result.status, "unsupported")
            self.assertEqual(result.source, source)
        source="x=1  # type: ignore\n"
        result = format_result(source)
        if result.status == "applied":
            self.assertEqual(ast.dump(ast.parse(source,type_comments=True)), ast.dump(ast.parse(result.source,type_comments=True)))
        else:
            self.assertEqual(result.source, source)

    def test_builder_excludes_unchanged_and_unsupported_positives(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            manifest=root/"manifest.jsonl"
            manifest.write_text(json.dumps({"name":"owned","url":"https://example.test/owned.git","revision":"a"*40,"license":"MIT","partition":"train"})+"\n")
            project=CorpusProject("owned","https://example.test/owned.git","a"*40,"MIT",partition="train")
            source="def run():\n    x = 1\n    return eval('x')\n"
            item=CuratedInput(project,"owned.py",FixtureInput("source",source,{}),canonical_hash(source),"train",raw_hash(source))
            with patch("codegraph.corpus_builder._uncurated_inputs",return_value=[item]):
                build_corpus(manifest,root/"release")
            rows=[json.loads(s) for s in (root/"release/views.jsonl").read_text().splitlines()]
            self.assertFalse(any(r["view_kind"] in {"renamed","formatted"} for r in rows))
            original=next(r for r in rows if r["view_kind"]=="source")
            self.assertTrue(any(g.get("reason")=="dynamic_or_reflective_call" for g in original["metadata"]["transformation_gaps"]))
            self.assertTrue(GRAPH_PIPELINE_VERSION.endswith("transform-v3"))
