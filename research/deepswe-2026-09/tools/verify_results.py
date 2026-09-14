"""Recompute selected-test rewards and reconcile exported three-arm measurements."""
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]

def read(name):
    return json.loads((PACKAGE / name).read_text(encoding='utf8'))

def verify():
    data = read('graded-outcomes.json')
    catalog = read(data['catalog'])
    assert data['default_test_status'] == 'passed' and data['test_index_base'] == 0
    observed = {}
    for row in data['outcomes']:
        key = (row['arm'], row['attempt'])
        assert key not in observed
        observed[key] = row
        names = catalog[row['task']]
        statuses = ['passed'] * len(names)
        seen = set()
        for item in row['nonpassing']:
            idx = item['test_index']
            assert 0 <= idx < len(names) and idx not in seen and item['status'] != 'passed'
            seen.add(idx)
            statuses[idx] = item['status']
        reward = row['reward']
        for group in ('f2p', 'p2p'):
            indices = [i for i, name in enumerate(names) if name.startswith('[' + group + '] ')]
            assert reward[group + '_total'] == len(indices)
            assert reward[group + '_passed'] == sum(statuses[i] == 'passed' for i in indices)
        assert reward['reward'] == int(reward['f2p_total'] > 0 and reward['f2p_passed'] == reward['f2p_total'] and reward['p2p_passed'] == reward['p2p_total'])
        assert row['helpers'] + 1 == len(row['session_usage'])
        for session in row['session_usage']:
            usage = session['usage']
            if usage:
                assert usage['input_tokens'] >= usage['cached_input_tokens'] >= 0 and usage['output_tokens'] >= 0
    results = read('results.json')
    for pair in results.get('pairs', []):
        for arm, label in [('none', 'none'), ('current', 'previous'), ('updated', 'revised')]:
            r = pair['arms'][arm]
            raw = observed[(label, r['attempt'])]
            for field in ('status', 'reward', 'native_seconds', 'helpers', 'patch_bytes'):
                assert r[field] == raw[field], (label, r['attempt'], field)
            for token in ('input_tokens', 'cached_input_tokens', 'output_tokens'):
                assert r['usage'][token] == sum(s['usage'][token] for s in raw['session_usage'] if s['usage']), (label, token)
    if results.get('state') == 'completed':
        assert len(observed) == 54 and results['completed_triplets'] == 18
        for arm, label in [('none', 'none'), ('current', 'previous'), ('updated', 'revised')]:
            rows = [r for (a, _), r in observed.items() if a == label]
            total = results['totals'][arm]
            assert len(rows) == total['attempts'] == 18
            assert total['complete_passes'] == sum(r['reward']['reward'] for r in rows)
            assert total['timeouts'] == sum(r['status'] == 'timeout' for r in rows)
            assert total['helpers'] == sum(r['helpers'] for r in rows)
            for token in ('input_tokens', 'cached_input_tokens', 'output_tokens'):
                assert total['usage'][token] == sum(s['usage'][token] for r in rows for s in r['session_usage'] if s['usage'])
    print(json.dumps({'status': 'verified', 'state': data['state'], 'graded_outcomes': len(observed),
        'selected_test_names': sum(len(v) for v in catalog.values())}))

if __name__ == '__main__':
    verify()
