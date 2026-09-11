import unittest

from codegraph.release_audit import coverage


class ReleaseAuditTest(unittest.TestCase):
    def test_gaps_count_inputs_not_repeated_units_and_detect_split_leaks(self):
        def row(split):
            return {"project": "owned", "split": split, "view_kind": "input:source",
                    "metadata": {"split_group": "owned", "source_artifact_id": "source",
                                 "semantic_trainable": True,
                                 "transformation_gaps": [{"view": "renamed", "status": "unsupported",
                                                           "reason": "dynamic_scope"}]}}
        result = coverage([row("train"), row("train"), row("test")])
        self.assertEqual(result["retained_source_inputs"], 1)
        self.assertEqual(result["transformation_gaps"], {"renamed/unsupported/dynamic_scope": 1})
        self.assertEqual(result["split_group_leaks"], {"owned": ["test", "train"]})
        self.assertEqual(result["semantic_views_by_split"], {"train": 2, "test": 1})

    def test_empty_coverage_does_not_invent_counts(self):
        result = coverage([])
        self.assertEqual(result["retained_source_inputs"], 0)
        self.assertEqual(result["semantic_views_by_split"], {})
