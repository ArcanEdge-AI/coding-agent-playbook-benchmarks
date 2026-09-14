"""Offline unit tests; no models, credentials, network, or repository writes."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from validate_plan import ROOT, check_repository, validate_manifest, validate_protocol, _unique_keys


def load(relative):
    return json.loads((ROOT / relative).read_text(encoding='utf-8'))


class PlanningValidationTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load('benchmarks/v1/manifest.json')
        self.protocol = load('protocols/initial-globals-delegation.json')

    def test_checked_in_metadata(self):
        self.assertEqual(check_repository(ROOT), [])

    def test_duplicate_task_id(self):
        self.manifest['tasks'][1]['id'] = self.manifest['tasks'][0]['id']
        self.assertTrue(validate_manifest(self.manifest))

    def test_incomplete_backlog(self):
        self.manifest['tasks'].pop()
        self.assertTrue(validate_manifest(self.manifest))

    def test_missing_acceptance_evidence(self):
        self.manifest['tasks'][0]['acceptance_evidence'] = ''
        self.assertTrue(validate_manifest(self.manifest))

    def test_assigned_split_needs_provenance(self):
        self.manifest['tasks'][0]['split'] = 'confirmation'
        self.assertTrue(validate_manifest(self.manifest))

    def test_source_family_must_not_cross_splits(self):
        for task, split in zip(self.manifest['tasks'][:2], ('development', 'confirmation')):
            task.update(split=split, source_family='same-problem-family', package_ref='opaque-reference')
        self.assertTrue(validate_manifest(self.manifest))

    def test_unassigned_task_cannot_be_smoke(self):
        self.manifest['smoke_task_ids'] = ['FIX-01']
        self.assertTrue(validate_manifest(self.manifest))

    def test_no_false_readiness(self):
        self.manifest['ready_for_scored_execution'] = True
        self.assertTrue(validate_manifest(self.manifest))

    def test_templates_cannot_authorize_inference(self):
        self.protocol['inference_authorized'] = True
        self.assertTrue(validate_protocol(self.protocol))

    def test_unvalidated_runtime_is_explicit(self):
        self.protocol['runtime']['validated'] = True
        self.assertTrue(validate_protocol(self.protocol))

    def test_budget_not_silently_approved(self):
        self.protocol['budget']['approved_total_credits'] = 100
        self.assertTrue(validate_protocol(self.protocol))

    def test_a_and_c_have_helpers_b_does_not(self):
        for index, value in ((0, False), (1, True), (2, False)):
            with self.subTest(index=index):
                changed = copy.deepcopy(self.protocol)
                changed['conditions'][index]['helpers_enabled'] = value
                self.assertTrue(validate_protocol(changed))

    def test_helper_route_is_tool_matched(self):
        self.protocol['conditions'][0]['helper_route'] = 'different'
        self.assertTrue(validate_protocol(self.protocol))

    def test_wrong_causal_contrast(self):
        self.protocol['primary_contrasts'] = [['A', 'B']]
        self.assertTrue(validate_protocol(self.protocol))

    def test_attempt_arithmetic(self):
        self.protocol['stages'][0]['author_attempts'] = 13
        self.assertTrue(validate_protocol(self.protocol))

    def test_boolean_not_a_count(self):
        self.protocol['stages'][0]['repeats'] = True
        self.assertTrue(validate_protocol(self.protocol))

    def test_duplicate_stage(self):
        self.protocol['stages'].append(copy.deepcopy(self.protocol['stages'][0]))
        self.assertTrue(validate_protocol(self.protocol))

    def test_candidate_capabilities_must_remain_unresolved(self):
        candidate = load('protocols/candidate-vs-incumbent.json')
        candidate['conditions'][1]['helpers_enabled'] = True
        self.assertTrue(validate_protocol(candidate))

    def test_malformed_container_types(self):
        for value in (None, [], 'not an object', 42):
            with self.subTest(value=value):
                self.assertTrue(validate_manifest(value))
                self.assertTrue(validate_protocol(value))
        self.manifest['tasks'][0] = []
        self.assertTrue(validate_manifest(self.manifest))
        self.protocol['stages'][0] = []
        self.assertTrue(validate_protocol(self.protocol))

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError):
            json.loads('{"status":"draft","status":"approved"}', object_pairs_hook=_unique_keys)

    def test_missing_files_are_reported(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(len(check_repository(Path(folder))), 3)


if __name__ == '__main__':
    unittest.main()
