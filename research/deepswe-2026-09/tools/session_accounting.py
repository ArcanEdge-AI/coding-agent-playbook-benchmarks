"""Account for native parent/child usage without counting inherited fork history."""
import json
from pathlib import Path

TOKEN_KEYS = ('input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens')


def events(path):
    return [json.loads(line) for line in path.read_text(encoding='utf8').splitlines() if line.strip()]


def sessions(folder):
    by_id = {}
    for path in sorted((folder / 'agent/sessions').rglob('*.jsonl')):
        stream = events(path)
        meta = next(e['payload'] for e in stream if e.get('type') == 'session_meta')
        sid = meta['id']
        assert sid not in by_id, ('Duplicate native session id', sid)
        contexts = [e['payload'] for e in stream if e.get('type') == 'turn_context']
        by_id[sid] = {'path': path, 'events': stream, 'meta': meta, 'contexts': contexts}
    roots = [sid for sid, d in by_id.items() if not d['meta'].get('parent_thread_id')]
    assert len(roots) == 1, ('Expected one native root', roots)
    result = []
    for sid, data in by_id.items():
        parent = data['meta'].get('parent_thread_id')
        inherited = set()
        ancestors = []
        cursor = parent
        while cursor:
            assert cursor in by_id and cursor not in ancestors, ('Missing or cyclic lineage', sid, cursor)
            ancestors.append(cursor)
            inherited.update(c.get('turn_id') for c in by_id[cursor]['contexts'])
            cursor = by_id[cursor]['meta'].get('parent_thread_id')
        own_contexts = [c for c in data['contexts'] if c.get('turn_id') not in inherited]
        own_turns = {c.get('turn_id') for c in own_contexts}
        active = not parent
        previous = {k: 0 for k in TOKEN_KEYS}
        usage = None
        anomalies = []
        updates = 0
        own_start = None
        own_end = None
        for event in data['events']:
            payload = event.get('payload') or {}
            if event.get('type') == 'turn_context' and payload.get('turn_id') in own_turns:
                active = True
                if own_start is None:
                    own_start = event.get('timestamp')
            if not active:
                continue
            if own_start is not None:
                own_end = event.get('timestamp')
            if event.get('type') != 'event_msg' or payload.get('type') != 'token_count':
                continue
            info = payload.get('info') or {}
            total, last = info.get('total_token_usage'), info.get('last_token_usage')
            if not total:
                continue
            current = {k: total.get(k, 0) for k in TOKEN_KEYS}
            if current == previous:
                continue  # Repeated terminal usage notification, not another request.
            delta = {k: current[k] - previous[k] for k in TOKEN_KEYS}
            if any(v < 0 for v in delta.values()):
                anomalies.append({'timestamp': event.get('timestamp'), 'kind': 'nonmonotonic cumulative usage'})
            if last and any(delta[k] != last.get(k, 0) for k in TOKEN_KEYS):
                anomalies.append({'timestamp': event.get('timestamp'), 'kind': 'cumulative delta differs from last request',
                                  'delta': delta, 'last': {k: last.get(k, 0) for k in TOKEN_KEYS}})
            previous, usage = current, current
            updates += 1
        if usage:
            assert usage['cached_input_tokens'] <= usage['input_tokens']
        result.append({'id': sid, 'parent_id': parent, 'depth': len(ancestors),
            'path': str(data['path']), 'own_turn_ids': sorted(own_turns),
            'models': sorted({c.get('model') for c in own_contexts}),
            'efforts': sorted({c.get('effort') for c in own_contexts}),
            'own_context_start': own_start, 'last_native_event': own_end,
            'usage': usage, 'distinct_usage_updates': updates, 'accounting_anomalies': anomalies,
            'inherited_contexts_excluded': len(data['contexts']) - len(own_contexts),
            'source': data['meta'].get('source')})
    root = next(r for r in result if r['parent_id'] is None)
    helpers = [r for r in result if r['parent_id'] is not None]
    observed = [r for r in result if r['usage'] is not None]
    return {'root': root, 'helpers': helpers, 'sessions': result,
            'helper_count': len(helpers),
            'helper_routes_compliant': all(r['models'] == ['gpt-5.6-luna'] and r['efforts'] == ['max']
                                           for r in helpers if r['own_turn_ids']),
            'all_agent_usage': {k: sum(r['usage'][k] for r in observed) for k in TOKEN_KEYS},
            'helper_usage': {k: sum((r['usage'] or {}).get(k, 0) for r in helpers) for k in TOKEN_KEYS},
            'usage_missing_session_ids': [r['id'] for r in result if r['usage'] is None],
            'accounting_anomaly_count': sum(len(r['accounting_anomalies']) for r in result)}


if __name__ == '__main__':
    import sys
    report = sessions(Path(sys.argv[1]))
    print(json.dumps(report, indent=2))
