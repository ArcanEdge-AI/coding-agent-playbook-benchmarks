"""Small hand-calculated fixtures for the research usage-accounting boundary."""
import json
from pathlib import Path
import tempfile
import unittest
from session_accounting import sessions


def context(turn, effort='high'):
    return {'type': 'turn_context', 'timestamp': '2026-09-13T00:00:00Z',
            'payload': {'turn_id': turn, 'model': 'gpt-5.6-luna', 'effort': effort}}


def usage(inputs, outputs, cached=0):
    counts = {'input_tokens': inputs, 'output_tokens': outputs, 'cached_input_tokens': cached,
              'reasoning_output_tokens': 0}
    return {'type': 'event_msg', 'payload': {'type': 'token_count',
            'info': {'total_token_usage': counts, 'last_token_usage': counts}}}


def write(folder, sid, parent, body):
    meta = {'type': 'session_meta', 'payload': {'id': sid, 'parent_thread_id': parent}}
    path = folder / 'agent/sessions' / (sid + '.jsonl')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(json.dumps(x) for x in [meta, *body]), encoding='utf8')


class AccountingTests(unittest.TestCase):
    def test_fork_history_and_repeated_totals_are_not_added(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            inherited = [context('root-turn'), usage(100, 10, 40)]
            write(folder, 'root', None, inherited + [usage(100, 10, 40)])
            write(folder, 'child', 'root', inherited + [context('child-turn', 'max'),
                                                        usage(50, 5, 20), usage(50, 5, 20)])
            result = sessions(folder)
            self.assertEqual(result['all_agent_usage']['input_tokens'], 150)
            self.assertEqual(result['all_agent_usage']['output_tokens'], 15)
            self.assertEqual(result['helper_usage']['input_tokens'], 50)
            self.assertEqual(result['helper_count'], 1)
            self.assertEqual(result['helpers'][0]['own_turn_ids'], ['child-turn'])
            self.assertEqual(result['helpers'][0]['distinct_usage_updates'], 1)
            self.assertTrue(result['helper_routes_compliant'])
            self.assertEqual(result['accounting_anomaly_count'], 0)

    def test_child_with_no_own_usage_is_missing_not_inherited_consumption(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            inherited = [context('root-turn'), usage(100, 10)]
            write(folder, 'root', None, inherited)
            write(folder, 'child', 'root', inherited + [context('child-turn', 'max')])
            result = sessions(folder)
            self.assertEqual(result['usage_missing_session_ids'], ['child'])
            self.assertEqual(result['all_agent_usage']['input_tokens'], 100)
            self.assertIsNone(result['helpers'][0]['usage'])

    def test_record_routing_mismatch_without_discarding_usage(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            write(folder, 'root', None, [context('root-turn'), usage(100, 10)])
            write(folder, 'child', 'root', [context('child-turn', 'high'), usage(50, 5)])
            result = sessions(folder)
            self.assertFalse(result['helper_routes_compliant'])
            self.assertEqual(result['all_agent_usage']['input_tokens'], 150)


if __name__ == '__main__':
    unittest.main()
