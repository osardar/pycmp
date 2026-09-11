import json
from pathlib import Path
import tempfile
import unittest

from codegraph.release_baseline import run


class ReleaseBaselineTest(unittest.TestCase):
    def test_refuses_overwrite_before_reading_inputs(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with self.assertRaisesRegex(ValueError, "new baseline"):
                run(root / "missing", root / "missing.json", root)

    def test_failed_audit_cannot_start_training(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            audit = root / "audit.json"
            audit.write_text(json.dumps({"static_gates_pass": False}))
            with self.assertRaisesRegex(ValueError, "did not pass"):
                run(root, audit, root / "output")
            self.assertFalse((root / "output").exists())
