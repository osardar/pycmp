import contextlib
import hashlib
import importlib.util
import io
import json
import marshal
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import torch

from pycmp_vectorizer import Vectorizer
from pycmp_vectorizer.cli import main
from pycmp_vectorizer.inference import Encoder, digest
from pycmp_vectorizer.runtime import parse
from pycmp_vectorizer.vendor.ast_normalize import ASTNormalizer
from pycmp_vectorizer.vendor.bytecode_reference import graph_code
from pycmp_vectorizer.vendor.shared_model import SharedGraphEncoder, FEATURE_KEYS
from pycmp_vectorizer.vendor.limits import LimitedList, reset


class VectorizerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name).resolve()
        cls.checkpoint = cls.root / "model.pt"
        torch.manual_seed(0)
        cls.model = SharedGraphEncoder(dimension=8, layers=1).eval()
        torch.save({"format": 2, "model": cls.model.state_dict(), "config": {
            "schema_version": 3, "feature_keys": list(FEATURE_KEYS), "dimension": 8,
            "layers": 1, "node_buckets": 2048, "relation_buckets": 512}}, cls.checkpoint)
        cls.vectorizer = Vectorizer(cls.checkpoint, host_runtime=True, include_units=True)

    @classmethod
    def tearDownClass(cls):
        cls.vectorizer.close()
        cls.temp.cleanup()

    def source(self, name, raw):
        path = self.root / name
        path.write_bytes(raw)
        return path

    def test_source_vector_parity_and_units(self):
        raw = b'def f(x):\n    return x+123\n'
        result = self.vectorizer.vectorize_file(self.source('parity.py', raw))
        self.assertEqual(result['status'], 'ok', result)
        graphs = ASTNormalizer().unit_graphs(raw.decode(), origin='input.py')
        with torch.inference_mode():
            expected = torch.nn.functional.normalize(self.model(graphs).mean(0), dim=0)
        self.assertTrue(torch.allclose(torch.tensor(result['vector']), expected, atol=1e-6))
        self.assertEqual(len(result['units']), len(graphs))
        self.assertAlmostEqual(sum(v*v for v in result['vector']), 1, places=5)
        self.assertEqual(result['input_sha256'], hashlib.sha256(raw).hexdigest())

    def test_bytecode_and_side_effect_nonexecution(self):
        target = self.root / 'MUST_NOT_EXIST'
        source = "open(%r, 'w').write('bad')\ndef f(x):\n    return x+1\n" % str(target)
        code = compile(source, 'owned.py', 'exec')
        raw = importlib.util.MAGIC_NUMBER + bytes(12) + marshal.dumps(code)
        result = self.vectorizer.vectorize_file(self.source('owned.pyc', raw))
        self.assertEqual(result['status'], 'ok', result)
        self.assertEqual(result['lane'], 'bytecode')
        self.assertFalse(target.exists())
        source_result = self.vectorizer.vectorize_file(self.source('owned.py',source.encode()))
        self.assertEqual(source_result['status'], 'ok')
        self.assertFalse(target.exists())
        self.assertNotEqual(result['embedding_profile_id'],source_result['embedding_profile_id'])

    def test_encoding_and_invalid_source(self):
        good = self.vectorizer.vectorize_file(self.source('latin.py', b'# coding: latin-1\ns="caf\xe9"\n'))
        self.assertEqual(good['status'],'ok',good)
        bad = self.vectorizer.vectorize_file(self.source('broken.py', b'def :'))
        self.assertEqual(bad['error']['code'],'invalid_source')
        self.assertNotIn('vector',bad)

    def test_limits_and_unsupported(self):
        for name,raw,expected in [('large.py',b'#'*65537,'input_limit'),
            ('short.pyc',b'bad','invalid_input'),('unknown.pyc',b'BAD!'+bytes(12),'unsupported_runtime'),
            ('notes.txt',b'hello','unsupported_format')]:
            result=self.vectorizer.vectorize_file(self.source(name,raw))
            self.assertEqual(result['error']['code'],expected,result)
            self.assertNotIn('vector',result)

    def test_symlink_and_fifo_rejection(self):
        original=self.source('target.py',b'x=1')
        linked=self.root/'link.py'; linked.symlink_to(original)
        self.assertEqual(self.vectorizer.vectorize_file(linked)['error']['code'],'symlink')
        fifo=self.root/'pipe.py'; os.mkfifo(fifo)
        self.assertEqual(self.vectorizer.vectorize_file(fifo)['error']['code'],'not_regular')

    def test_duplicate_cache_and_summary(self):
        a=self.source('dup1.py',b'value=4321'); b=self.source('dup2.py',b'value=4321')
        records=list(self.vectorizer.vectorize_paths([a,b]))
        self.assertEqual(records[0]['vector'],records[1]['vector'])
        self.assertNotEqual(records[0]['input_path'],records[1]['input_path'])
        self.assertTrue(records[1]['cache_hit'])
        self.assertEqual(self.vectorizer.summary['counts']['succeeded'],2)
        self.assertEqual(self.vectorizer.summary['completion'],'complete')

    def test_directory_skips_and_empty(self):
        root=self.root/'empty'; root.mkdir()
        (root/'readme.txt').write_text('notes')
        self.assertEqual(list(self.vectorizer.vectorize_paths([root])),[])
        self.assertEqual(self.vectorizer.summary['counts']['skipped'],1)
        self.assertEqual(self.vectorizer.summary['counts']['candidates'],0)

    def test_profile_and_known_bytecode_collisions(self):
        first=graph_code(compile('def f():\n return 1','owned','exec'), 'owned')
        second=graph_code(compile('def f():\n return 2','owned','exec'), 'owned')
        self.assertEqual(first,second)
        if sys.version_info >= (3,11):
            a=graph_code(compile('def f(x,y):\n return x+y','owned','exec'),'owned')
            b=graph_code(compile('def f(x,y):\n return x-y','owned','exec'),'owned')
            self.assertEqual(a,b)

    def test_formatting_and_rename_invariance(self):
        a=self.vectorizer.vectorize_file(self.source('rename1.py', b'def f(x):\n return x+1\n'))
        b=self.vectorizer.vectorize_file(self.source('rename2.py', b'def f( renamed ):\n    return renamed + 1\n'))
        self.assertEqual(a['vector'],b['vector'])

    def test_construction_edge_limit(self):
        reset(1,1)
        edges=LimitedList('edges'); edges.append('one')
        with self.assertRaisesRegex(ValueError,'edge_limit'):edges.append('two')

    def test_parser_timeout(self):
        result=parse(sys.executable,'source',b'x=1',timeout=.000001)
        self.assertEqual(result['error'],'timeout')

    def test_inference_timeout_and_recovery(self):
        old=self.vectorizer.encoder.timeout
        self.vectorizer.encoder.timeout=0
        try:
            result=self.vectorizer.vectorize_file(self.source('inference-timeout.py',b'x=797979'))
            self.assertEqual(result['error']['code'],'timeout')
        finally:
            self.vectorizer.encoder.timeout=old
        result=self.vectorizer.vectorize_file(self.source('timeout-recovery.py',b'x=797978'))
        self.assertEqual(result['status'],'ok')

    def test_interrupted_stream_summary_is_partial(self):
        path=self.source('interrupt.py',b'x=45454')
        stream=self.vectorizer.vectorize_paths([path,path])
        next(stream)
        self.assertEqual(self.vectorizer.summary['completion'],'partial')
        stream.close()

    def test_snapshot_mismatch_and_default_inventory(self):
        from pycmp_vectorizer import runtime
        with patch.object(runtime,'sha',return_value='mismatch'):
            with self.assertRaisesRegex(ValueError,'snapshot mismatch'):
                runtime.verify_snapshot()
        with patch.dict(os.environ,{},clear=True):
            with self.assertRaisesRegex(ValueError,'all seven pinned runtimes'):
                Vectorizer(self.checkpoint)

    def test_cache_lru_bound(self):
        # Exercise eviction without spending time repeatedly encoding fixtures.
        vectorizer=self.vectorizer
        vectorizer.cache.clear();vectorizer.cache_bytes=0
        with patch('pycmp_vectorizer.api.runtime.parse',return_value={'ok':True}), \
             patch.object(vectorizer.encoder,'encode',return_value={'vector':[1.]+[0.]*7,
                'node_count':2,'edge_count':1,'unit_count':1,'graph_sha256':'owned'}):
            for i in range(130):
                vectorizer.vectorize_file(self.source('cache.py',('x=%d'%i).encode()))
        self.assertEqual(len(vectorizer.cache),128)
        self.assertLessEqual(vectorizer.cache_bytes,32*1024**2)
        vectorizer.cache.clear();vectorizer.cache_bytes=0

    def test_inference_restart_after_limit(self):
        old=self.vectorizer.encoder.rss_limit
        self.vectorizer.encoder.rss_limit=1
        try:
            result=self.vectorizer.vectorize_file(self.source('rss.py',b'value=9988'))
            self.assertEqual(result['error']['code'],'memory_limit',result)
        finally:
            self.vectorizer.encoder.rss_limit=old
        result=self.vectorizer.vectorize_file(self.source('restart.py',b'value=9989'))
        self.assertEqual(result['status'],'ok',result)

    def test_checkpoint_mismatch(self):
        bad=self.root/'bad.pt';torch.save({'format':0},bad)
        with self.assertRaisesRegex(ValueError,'schema mismatch'):
            Vectorizer(bad,host_runtime=True)

    def test_cli_jsonl_mixed_batch_and_overwrite(self):
        good=self.source('cli.py',b'x=100')
        bad=self.source('cli-bad.py',b'def :')
        output=self.root/'results.jsonl'
        args=['vectorize',str(good),str(bad),'--host-runtime','--checkpoint',str(self.checkpoint),'--output',str(output)]
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(args),2)
            before=output.read_bytes()
            self.assertEqual(main(args),1)
            self.assertEqual(before,output.read_bytes())
        rows=[json.loads(line) for line in before.splitlines()]
        self.assertEqual([r['record_type'] for r in rows],['file','file','summary'])
        self.assertEqual(rows[-1]['counts']['failed'],1)

    def test_cli_standalone_process(self):
        source=self.source('subprocess.py',b'def f(): return 5')
        result=subprocess.run([sys.executable,'-I','-m','pycmp_vectorizer','vectorize',str(source),
            '--host-runtime','--checkpoint',str(self.checkpoint),'--output','-'],cwd=self.root,
            capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stderr)
        records=[json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual(records[0]['status'],'ok')
        self.assertEqual(records[-1]['completion'],'complete')


if __name__ == '__main__':
    unittest.main()
