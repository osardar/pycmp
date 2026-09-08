import json
import sys
import types
import unittest
from unittest.mock import patch

from codegraph.fixture_obfuscation import obfuscate, negative_control
from codegraph.similarity_benchmark import FIXTURES, classify_reconstruction, RUNTIMES


def run_cases(modules, cases):
    loaded = {}
    for filename, source in modules.items():
        module = types.ModuleType(filename[:-3])
        loaded[filename[:-3]] = module
    with patch.dict(sys.modules, loaded):
        for name in sorted(loaded, key=lambda name: name == "main"):
            exec(compile(modules[name + ".py"], name + ".py", "exec"), loaded[name].__dict__)
        outcomes = []
        for case in cases:
            try:
                value = loaded["main"].run(case["input"])
                outcomes.append("error" not in case and value == case.get("expected"))
            except Exception as error:
                outcomes.append(type(error).__name__ == case.get("error"))
        return outcomes


class SimilarityBenchmarkTest(unittest.TestCase):
    def test_fixtures_and_all_obfuscation_seeds_preserve_oracles(self):
        projects = json.loads((FIXTURES / "manifest.json").read_text())
        self.assertEqual(len(projects), 10)
        for project in projects:
            if tuple(map(int, project["python_min"].split("."))) > sys.version_info[:2]:
                continue
            with self.subTest(project=project["name"]):
                modules = {name: (FIXTURES / project["name"] / name).read_text()
                           for name in project["modules"]}
                cases = json.loads((FIXTURES / project["name"] / "oracle.json").read_text())
                self.assertTrue(all(run_cases(modules, cases)))
                for level in ("light", "structural"):
                    for seed in (0, 1, 2):
                        transformed, mapping = obfuscate(modules, level=level, seed=seed)
                        self.assertTrue(all(run_cases(transformed, cases)), (project["name"], level, seed))
                        self.assertEqual((transformed, mapping), obfuscate(modules, level=level, seed=seed))
                        self.assertNotEqual(transformed, modules)
                        generated = FIXTURES / "generated" / project["name"] / ("obfuscated-" + level + "-" + str(seed))
                        self.assertEqual(transformed, {name: (generated / name).read_text() for name in modules})
                        self.assertEqual(mapping, json.loads((generated / "transformation.json").read_text()))
                self.assertFalse(all(run_cases(negative_control(modules), cases)))

    def test_reconstruction_exit_zero_requires_behavior_and_complete_output(self):
        ok = {"status": "ok", "returncode": 0, "stdout": "def run(x): return x", "stderr": ""}
        verified = {"status": "ok", "response": {"passed": True}}
        self.assertEqual(classify_reconstruction(ok, verified), "success")
        self.assertEqual(classify_reconstruction(ok, {"status": "ok", "response": {"passed": False}}),
                         "behavior_mismatch")
        self.assertEqual(classify_reconstruction({**ok, "stderr": "Unsupported opcode"}, verified), "unsupported")
        self.assertEqual(classify_reconstruction({**ok, "status": "timeout"}, None), "timeout")
        self.assertEqual(classify_reconstruction({**ok, "stdout": "# no reconstruction\n"}, verified),
                         "invalid_output")

    def test_matrix_has_111_combinations_and_true_legacy_runtime(self):
        projects = json.loads((FIXTURES / "manifest.json").read_text())
        count = sum(3 for project in projects for runtime in RUNTIMES
                    if tuple(map(int, runtime.split("."))) >=
                    tuple(map(int, project["python_min"].split("."))))
        self.assertEqual(count, 111)
        self.assertIn("3.4.10", RUNTIMES["3.4"])
