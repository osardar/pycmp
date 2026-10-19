import importlib.util
import marshal
from pathlib import Path
import tempfile
import subprocess
import unittest
from unittest.mock import patch, Mock

from codegraph._compiled_worker import decode, graph_code, bounded_item
from codegraph.compiled_retrieval import (Budget, Limit, Ledger, assignment, aggregate, bundle_queries,
                                         ranked, tensor_facts, fingerprint, CONFIGS)
from codegraph.semantic import ProgramGraph, GraphNode
from codegraph.shared_model import SharedGraphEncoder
from codegraph import compiled_retrieval as expanded


class ExpandedRetrievalTest(unittest.TestCase):
    def test_timeout_kills_child_process_group(self):
        proc = Mock(pid=123)
        proc.communicate.side_effect = subprocess.TimeoutExpired('owned-worker', .01)
        with patch('codegraph._compiled_worker.subprocess.Popen', return_value=proc), \
             patch('codegraph._compiled_worker.os.killpg') as kill:
            self.assertEqual(bounded_item({'mode':'compile'}, seconds=.01), {'status':'timeout'})
        kill.assert_called_once()
        proc.wait.assert_called_once()

    def test_checkpoint_mismatch_fails_before_workers(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(expanded, 'sha', return_value='actual'), \
                 patch.object(expanded, 'load', return_value={'reserved_hardpair_families_accessed':False,
                    'preflight':{'checkpoints':[{'sha256':'expected'}]*3}}), \
                 patch.object(expanded, 'runtime_inventory') as inventory:
                with self.assertRaisesRegex(ValueError, 'checkpoint mismatch'):
                    expanded.initialize(root/'parent',root/'output',[root/'model']*3,False)
                inventory.assert_not_called()

    def test_file_evaluation_resume_equivalence(self):
        configs = (("3.14", 0), ("3.14", 1))
        owner = {"repository": "owned", "split": "test", "split_group": "owned"}
        manifest = {"gallery": [{"gallery_id": s, "source_sha256": s,
                                "owners": [dict(owner, split_group=s)]} for s in ("a", "b")],
                    "observations": [{"origin": "a", "source": "a", "owner": owner,
                        "recipes": [{"family": "unchanged", "status": "unchanged", "actual_dose": None}]}]}
        class Interrupt:
            calls = 0
            def check(self):
                self.calls += 1
                if self.calls == 3:
                    raise Limit("owned interruption")
        with tempfile.TemporaryDirectory() as directory, patch.object(expanded, "CONFIGS", configs):
            root = Path(directory)
            outputs = []
            for interrupted in (False, True):
                path = root / (str(interrupted) + '.sqlite')
                ledger = Ledger(path)
                for source, vector in (("a", [1.,0.]), ("b", [0.,1.])):
                    for runtime,opt in configs:
                        ledger.put('compile', source+str(opt), {'source':source,'runtime':runtime,
                            'optimization':opt,'status':'decoded','artifact_sha256':source})
                    ledger.put('embedding', source, {'artifact':source,
                        'vectors':{m:vector for m in expanded.METHODS[:-1]},
                        'opcode_structure':{source:1},'facts':{'tensors':source,'features':source}})
                if interrupted:
                    with self.assertRaises(Limit):
                        expanded.evaluate_files(manifest,ledger,Interrupt())
                    self.assertEqual(len(list(ledger.rows('file-cell'))),1)
                    ledger.close()
                    ledger = Ledger(path)
                expanded.evaluate_files(manifest,ledger,Budget(root,30))
                outputs.append(list(ledger.rows('file')))
                self.assertEqual(len(list(ledger.rows('file-cell'))),4)
                ledger.close()
            self.assertEqual(outputs[0], outputs[1])

    def test_decode_does_not_execute_and_rejects_malformed_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            sentinel = Path(directory) / "EXECUTED"
            source = "open(%r, 'w').write('executed')\ndef f(x):\n    return x+1\n" % str(sentinel)
            raw = importlib.util.MAGIC_NUMBER + bytes(12) + marshal.dumps(compile(source, 'owned.py', 'exec'))
            graph = ProgramGraph.from_dict(decode(raw))
            self.assertEqual(graph.metadata['parse_status'], 'valid')
            self.assertFalse(sentinel.exists())
            for invalid in (raw[:10], b'BAD!'+raw[4:], raw[:-5], raw+b'garbage'):
                with self.assertRaises((ValueError, EOFError, TypeError)):
                    decode(invalid)

    def test_optimization_and_control_evidence(self):
        source = '"""module docs"""\ndef f(x):\n    assert x\n    if x > 2:\n        return 1\n    return 0\n'
        graphs = [graph_code(compile(source, 'owned.py', 'exec', optimize=opt), 'owned') for opt in range(3)]
        self.assertTrue(any(e['kind']=='control_branch' for e in graphs[0]['edges']))
        self.assertNotEqual(fingerprint(graphs[0]), fingerprint(graphs[2]))

    def test_assignment_beats_greedy_and_handles_rectangles(self):
        values = [[.9, .8], [.85, .1], [-.1, -.2]]
        pairs = assignment(values)
        self.assertAlmostEqual(sum(p[2] for p in pairs), 1.65)
        self.assertEqual(len({p[0] for p in pairs}), len(pairs))
        self.assertEqual(len({p[1] for p in pairs}), len(pairs))
        self.assertEqual(assignment([[-.1]]), [])
        scores, _ = aggregate(values, [1, 1, 1])
        self.assertAlmostEqual(scores['assignment'], 1.65/3)
        self.assertEqual(scores['maximum'], .9)

    def test_ties_ambiguous_origins_and_missing_origin(self):
        self.assertEqual(ranked([1,1], ['a','b'], {'a'}, {'a'})['rank'], 2)
        self.assertEqual(ranked([1,1], ['a','b'], {'a','b'}, {'a','b'})['rank'], 1)
        self.assertEqual(ranked([1], ['b'], {'a'}, {'a'})['status'], 'missing_origin')
        self.assertEqual(ranked([float('nan')], ['a'], {'a'}, {'a'})['status'], 'invalid_query')

    def test_tensor_fingerprint_includes_availability(self):
        model = SharedGraphEncoder(dimension=8, layers=1)
        first = ProgramGraph('a', 'module', [GraphNode('n0','core:function',{'semantic_kind':'function'},('semantic_kind',))], [])
        second = ProgramGraph('b', 'module', [GraphNode('n0','core:function',{'semantic_kind':'function'},())], [])
        self.assertEqual(tensor_facts(first, model)['features'], tensor_facts(second, model)['features'])
        self.assertNotEqual(tensor_facts(first, model)['tensors'], tensor_facts(second, model)['tensors'])

    def test_durable_ledger_and_cumulative_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ledger = Ledger(root/'ledger.sqlite')
            ledger.put('file', 'one', {'score': .5})
            ledger.close()
            resumed = Ledger(root/'ledger.sqlite')
            self.assertEqual(resumed.get('file','one'), {'score': .5})
            self.assertIsNone(resumed.get('file','pending'))
            resumed.close()
            with self.assertRaises(Limit):
                Budget(root, -1).check()
            with self.assertRaises(Limit):
                Budget(root, 100, disk=1).check()

    def test_bundle_sampling_nested_and_donor_splits(self):
        bundles = [{'repository': str(i), 'owner': {'repository':str(i),'split':'train' if i<2 else 'test', 'split_group':str(i)},
                    'sources': ['%d-%d'%(i,n) for n in range(10)]} for i in range(3)]
        manifest = {'bundles':bundles, 'observations':[], 'gallery':[]}
        queries = bundle_queries(manifest)
        self.assertEqual(queries, bundle_queries(manifest))
        removal = [q for q in queries if q['origin']=='0' and q['family']=='remove' and q['seed']==0]
        for left,right in zip(removal,removal[1:]):
            self.assertLessEqual(set(right['sources']),set(left['sources']))
        for query in queries:
            self.assertTrue(query['sources'])
            if query['origin']=='0':
                self.assertNotIn('2',query['donors'])
        self.assertEqual(len(CONFIGS)**2,441)


if __name__ == '__main__':
    unittest.main()
