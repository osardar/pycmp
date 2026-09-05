import py_compile
import unittest

from codegraph.ingest import ingest_path, ingest_source
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
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "sample.py"
            source.write_text(SOURCE)
            compiled = Path(directory) / "sample.pyc"
            py_compile.compile(str(source), cfile=str(compiled), doraise=True)
            result = ingest_path(compiled)
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
