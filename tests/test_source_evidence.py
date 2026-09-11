import ast
import json
import unittest

from codegraph.hardpair_diagnostics import facts
from codegraph.ingest import ingest_source
from codegraph.semantic import ProgramGraph
from codegraph.shared_model import SharedGraphEncoder
from codegraph.source_evidence import Bindings, field_evidence, field_inventory, typed_value
from codegraph.workflow import _load_model


MUTATIONS = {
    "number_value": ("x=40", "x=41"),
    "number_type": ("x=1", "x=1.0"),
    "byte_string": ("x='key'", "x=b'key'"),
    "boolean": ("x=True", "x=False"),
    "keyword": ("def run(x): return send(timeout=x)", "def run(x): return send(retries=x)"),
    "module": ("import math", "import os"),
    "import_symbol": ("from math import sqrt", "from os import unlink"),
    "relative_import": ("from .x import y", "from ..x import y"),
    "conversion": ("def run(x): return f'{x!r}'", "def run(x): return f'{x!s}'"),
    "conditional_body": ("if ready:\n def run(x): return x+1", "if ready:\n def run(x): return x-1"),
    "builtin": ("def run(x): return min(x)", "def run(x): return max(x)"),
    "exception": ("try: pass\nexcept ValueError: pass", "try: pass\nexcept TypeError: pass"),
    "singleton_pattern": ("match x:\n case True: pass", "match x:\n case False: pass"),
    "async_comprehension": ("async def f(xs): return [x for x in xs]", "async def f(xs): return [x async for x in xs]"),
    "global_target": ("a=1\nb=2\ndef f():\n global a\n a=3", "a=1\nb=2\ndef f():\n global b\n b=3"),
    "parameter_role": ("def f(a,b): return a-b", "def f(a,b): return b-a"),
    "decorator": ("@first\ndef f(): pass", "@second\ndef f(): pass"),
    "default": ("def f(a=2): return a", "def f(a=3): return a"),
}

RENAMES = {
    "shadowed_eval": ("def f(eval,x): return eval(x)", "def f(callback,x): return callback(x)"),
    "locals": ("def f(x):\n y=x+1\n return y", "def renamed(a):\n b=a+1\n return b"),
    "import_alias": ("import math as m\ndef f(x): return m.sqrt(x)", "import math as n\ndef f(y): return n.sqrt(y)"),
    "closure": ("def f(x):\n def g(y): return x+y\n return g(1)", "def a(p):\n def b(q): return p+q\n return b(1)"),
    "comprehension": ("def f(xs): return [x+1 for x in xs]", "def g(values): return [v+1 for v in values]"),
    "nonlocal": ("def f():\n x=1\n def g():\n  nonlocal x\n  x+=1\n  return x\n return g()", "def a():\n y=1\n def b():\n  nonlocal y\n  y+=1\n  return y\n return b()"),
}


class SourceEvidenceTest(unittest.TestCase):
    def fingerprints(self, source):
        model = SharedGraphEncoder(dimension=8, layers=2)
        return [facts(g, model)["tensors"] for g in ingest_source(source).graphs]

    def test_mutations_survive_consumed_tensor_encoding(self):
        for name, (left, right) in MUTATIONS.items():
            with self.subTest(name=name):
                self.assertNotEqual(self.fingerprints(left), self.fingerprints(right))

    def test_safe_renaming_preserves_consumed_tensors(self):
        for name, (left, right) in RENAMES.items():
            with self.subTest(name=name):
                self.assertEqual(self.fingerprints(left), self.fingerprints(right))

    def test_every_runtime_ast_field_has_storage_policy(self):
        inventory = {(r["node"], r["field"]) for r in field_inventory()}
        for name in dir(ast):
            cls = getattr(ast, name)
            if isinstance(cls, type) and issubclass(cls, ast.AST):
                for field in cls._fields:
                    self.assertIn((name, field), inventory)
        for source in [v for pair in MUTATIONS.values() for v in pair]:
            for node in ast.walk(ast.parse(source)):
                self.assertEqual(set(field_evidence(node)["ast_fields"]), set(node._fields))

    def test_literals_roundtrip_without_type_loss(self):
        values = [None, True, False, 1, 1.0, -0.0, 1j, b"\x00\xff", "\x00", Ellipsis, 1 << 20000]
        tokens = [json.dumps(typed_value(v), sort_keys=True) for v in values]
        self.assertEqual(len(tokens), len(set(tokens)))
        for graph in ingest_source("x = b'\\xff'\ny=1.0\nz=1j").graphs:
            self.assertEqual(graph.to_dict(), ProgramGraph.from_dict(json.loads(json.dumps(graph.to_dict()))).to_dict())

    def test_conditional_try_and_duplicate_declarations_are_units(self):
        source = "if flag:\n def f(): return 1\nelse:\n def f(): return 2\ntry:\n class C:\n  def m(self): return 3\nexcept Exception:\n pass\nx=lambda: 4\n"
        graphs = ingest_source(source).graphs
        names = [g.metadata["qualified_name"] for g in graphs]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(len(graphs), 6)
        references = {n.attributes["unit_ref"] for g in graphs for n in g.nodes if "unit_ref" in n.attributes}
        self.assertEqual(references, set(names))

    def test_shadowing_and_closure_bindings_are_conservative(self):
        source = "import math as m\ndef outer(min):\n def inner(x): return min(x)+m.sqrt(x)\n return inner\n"
        tree = ast.parse(source)
        bindings = Bindings(tree)
        names = [n for n in ast.walk(tree) if isinstance(n, ast.Name)]
        minimum = next(n for n in names if n.id == "min")
        self.assertNotIn("external_identity", bindings.attributes(minimum))
        self.assertIn("scope:1:function", bindings.attributes(minimum)["binding_identity"])
        attr = next(n for n in ast.walk(tree) if isinstance(n, ast.Attribute))
        self.assertEqual(bindings.attributes(attr)["external_identity"], "math.sqrt")
        for source in ("def f(x):\n y=min(x)\n min=x\n return y", "from unknown import *\nx=min(items)"):
            tree = ast.parse(source)
            b = Bindings(tree)
            minimum = next(n for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id == "min" and isinstance(n.ctx, ast.Load))
            self.assertNotIn("external_identity", b.attributes(minimum))

    def test_schema_two_graph_is_rejected(self):
        graph = ingest_source("x=1").graphs[0].to_dict()
        graph["schema_version"] = 2
        with self.assertRaisesRegex(ValueError, "unsupported graph schema"):
            ProgramGraph.from_dict(graph)

    def test_schema_two_checkpoint_is_rejected(self):
        from unittest.mock import patch
        with patch("codegraph.workflow.torch.load", return_value={"format": 2, "config": {"schema_version": 2}}):
            with self.assertRaisesRegex(ValueError, "incompatible"):
                _load_model("not-loaded.pt")

    def test_architecture_probes_preserve_inputs_and_weight_shapes(self):
        import torch
        from codegraph.source_audit import ConditionedLayer, reverse_ast, pool_score
        graph = ingest_source("def f(x): return x+1").graphs[-1]
        before = graph.to_dict()
        reverse = reverse_ast(graph)
        self.assertEqual(before, graph.to_dict())
        self.assertGreater(len(reverse.edges), len(graph.edges))
        from codegraph.shared_model import RelationalLayer
        original, changed = RelationalLayer(8), ConditionedLayer(8)
        changed.load_state_dict(original.state_dict())
        values = torch.randn(3, 8)
        edge = torch.tensor([[0, 1], [1, 2]])
        self.assertTrue(torch.isfinite(changed(values, edge, torch.randn(2, 8))).all())
        vectors = torch.nn.functional.normalize(torch.randn(3, 8), dim=-1)
        for method in ("baseline", "unit_matching"):
            self.assertAlmostEqual(pool_score(vectors, vectors, method), 1.0, places=6)

    def test_comprehension_outer_iterable_and_nonlocal_resolve_outer_scope(self):
        tree = ast.parse("def f(xs):\n y=0\n z=[x for x in xs]\n def g():\n  nonlocal y\n  y=1\n return z\n")
        b = Bindings(tree)
        iterable = next(n for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id == "xs")
        self.assertIn("scope:1:function", b.attributes(iterable)["binding_identity"])
        nonlocal_node = next(n for n in ast.walk(tree) if isinstance(n, ast.Nonlocal))
        self.assertIn("scope:1:function", b.attributes(nonlocal_node)["binding_identity"])
