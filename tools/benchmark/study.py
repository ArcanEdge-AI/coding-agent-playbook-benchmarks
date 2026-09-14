"""Offline comparison preparation, audited result intake, blinded review, and reports.

This module does not launch agents or authorize inference. Runtime evidence is a
separate gate; imported or simulated results cannot automatically promote globals.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from decimal import Decimal
import difflib
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import random
import secrets
import sys

from suite import (CATALOG, ROOT, Invalid, canonical, digest, load_catalog, lookup,
                   materialize, read_json, snapshot, write_new)

DIMENSIONS = ('architectural_fit', 'appropriate_complexity', 'clarity_changeability',
              'validation_delivery')


def positive_int(value, name):
    if type(value) is not int or value < 1:
        raise Invalid(f'{name} must be a positive integer.')


def schedule(catalog: dict, conditions: list[str], task_ids: list[str], repeats: int,
             seed: int, protocol: dict) -> dict:
    positive_int(repeats, 'repeats')
    if protocol.get('submission', {}).get('commit_required') is not False:
        raise Invalid('This adapter grades workspace snapshots, not committed submissions.')
    if type(seed) is not int or not conditions or len(set(conditions)) != len(conditions):
        raise Invalid('Invalid seed or duplicate conditions.')
    if not task_ids or len(set(task_ids)) != len(task_ids):
        raise Invalid('Select distinct tasks.')
    if protocol.get('comparison_kind') == 'globals_and_delegation':
        expected = [('A', 'none', True, 'shared'), ('B', 'non_delegation', False, None),
                    ('C', 'full', True, 'shared')]
    elif protocol.get('comparison_kind') == 'instruction_revision':
        expected = [('incumbent', 'incumbent', None, 'freeze_identically'),
                    ('candidate', 'candidate', None, 'freeze_identically')]
    else:
        raise Invalid('Unsupported comparison kind.')
    actual = [(c['id'], c['globals'], c['helpers_enabled'], c['helper_route']) for c in protocol['conditions']]
    if actual != expected:
        raise Invalid('Conditions no longer isolate the intended comparison.')
    if conditions != [c['id'] for c in protocol['conditions']]:
        raise Invalid('Condition IDs must match the complete protocol.')
    tasks = {task_id: lookup(catalog, task_id) for task_id in task_ids}
    if any(t['split'] != 'development' for t in tasks.values()):
        raise Invalid('This local preparer is for development tasks only.')
    rng = random.Random(seed)
    blocks = [(task_id, repeat) for task_id in task_ids for repeat in range(1, repeats + 1)]
    rng.shuffle(blocks)
    # Randomized cyclic Latin ordering balances condition launch positions to +/-1.
    offset_order = list(range(len(conditions))); rng.shuffle(offset_order)
    order = list(conditions); rng.shuffle(order)
    records = []
    for i, (task_id, repeat) in enumerate(blocks):
        offset = offset_order[i % len(conditions)]
        for condition in order[offset:] + order[:offset]:
            identity = {'task_id': task_id, 'repeat': repeat, 'condition': condition, 'seed': seed,
                        'catalog_sha256': digest(catalog), 'protocol_sha256': digest(protocol)}
            records.append({'run_id': digest(identity)[:24], 'task_id': task_id,
                            'repeat': repeat, 'condition': condition,
                            'task_sha256': tasks[task_id]['package_sha256'],
                            'evaluator_sha256': tasks[task_id]['evaluator_sha256'],
                            'checks_sha256': tasks[task_id]['checks_sha256'],
                            'source_family': tasks[task_id]['source_family'],
                            'submission_mode': tasks[task_id]['submission_mode'],
                            'helpers_enabled': next(c['helpers_enabled'] for c in protocol['conditions'] if c['id']==condition),
                            'root_model': protocol.get('main_model'), 'root_effort': protocol.get('main_reasoning_effort'),
                            'helper_model': protocol.get('helper_route',{}).get('model'),
                            'helper_effort': protocol.get('helper_route',{}).get('reasoning_effort')})
    result = {'schema_version': 1, 'status': 'prepared_not_authorized', 'seed': seed,
              'catalog_sha256': digest(catalog), 'protocol_sha256': digest(protocol),
              'conditions': conditions, 'task_ids': task_ids, 'repeats': repeats,
              'inference_authorized': False, 'runtime_validated': False,
              'runs': records, 'primary_contrasts': protocol['primary_contrasts']}
    result['schedule_sha256'] = digest(result)
    return result


def verify_schedule(doc: dict) -> None:
    expected = digest({k: v for k, v in doc.items() if k != 'schedule_sha256'})
    if doc.get('schedule_sha256') != expected:
        raise Invalid('Schedule changed after freezing.')
    if doc.get('inference_authorized') is not False or doc.get('runtime_validated') is not False:
        raise Invalid('Offline schedule cannot claim inference or runtime authorization.')
    keys = [(r['task_id'], r['repeat'], r['condition']) for r in doc['runs']]
    if len(set(keys)) != len(keys) or len({r['run_id'] for r in doc['runs']}) != len(keys):
        raise Invalid('Duplicate schedule slot.')
    expected_keys = {(t, n, c) for t in doc['task_ids'] for n in range(1, doc['repeats'] + 1)
                     for c in doc['conditions']}
    if set(keys) != expected_keys:
        raise Invalid('Incomplete or extra schedule slots.')


def prepare(catalog: dict, protocol: dict, task_ids: list[str], repeats: int,
            seed: int, out: Path) -> dict:
    if out.exists() or out.resolve() == ROOT or ROOT in out.resolve().parents:
        raise Invalid('Use a NEW study directory outside the repository.')
    doc = schedule(catalog, [c['id'] for c in protocol['conditions']], task_ids, repeats, seed, protocol)
    out.mkdir(parents=True)
    write_new(out / 'schedule.json', doc); write_new(out / 'protocol.json', protocol)
    write_new(out / 'catalog.json', catalog)
    (out / 'records').mkdir(); (out / 'reviews').mkdir()
    for run in doc['runs']:
        materialize(lookup(catalog, run['task_id']), out / 'workspaces' / run['run_id'])
    write_new(out / 'readiness.json', {'status': 'blocked_for_inference', 'model_calls': 0,
              'blockers': ['No approved inference budget or frozen runtime/model configuration.',
                           'Enabled and disabled native capability controls are not verified.',
                           'No sealed confirmation tasks or calibrated human-review policy.'],
              'note': 'Do not launch the archived runner. This directory contains offline workspaces only.'})
    return doc


def native_usage(trial: Path) -> dict:
    """Reuse the immutable archive parser; its schema still needs runtime revalidation."""
    parser_path = ROOT / 'research/deepswe-2026-09/tools/session_accounting.py'
    spec = importlib.util.spec_from_file_location('archived_session_accounting', parser_path)
    if spec is None or spec.loader is None:
        raise Invalid('Archived native parser unavailable.')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    parsed = module.sessions(trial)
    if parsed['accounting_anomaly_count']:
        raise Invalid('Native session accounting anomalies; do not estimate complete cost.')
    rows = []
    for s in parsed['sessions']:
        if len(s['models']) != 1 or len(s['efforts']) != 1:
            raise Invalid('A session changed model/effort or lacks a route; requires request-level accounting.')
        rows.append({'session_id': s['id'], 'parent_id': s['parent_id'],
                     'model': s['models'][0], 'effort': s['efforts'][0], 'tokens': s['usage']})
    sources = sorted((trial / 'agent/sessions').rglob('*.jsonl'))
    return {'usage_scope': 'own_session_only', 'complete': not parsed['usage_missing_session_ids'],
            'sessions': rows, 'parser_sha256': hashlib.sha256(parser_path.read_bytes()).hexdigest(),
            'native_evidence_sha256': digest([hashlib.sha256(p.read_bytes()).hexdigest() for p in sources]),
            'runtime_certified': False}


def price_usage(usage: dict, rates: dict) -> dict:
    if usage.get('usage_scope') != 'own_session_only' or type(usage.get('complete')) is not bool:
        raise Invalid('Usage must distinguish each session\'s own consumption and completeness.')
    sessions = usage.get('sessions')
    if not isinstance(sessions, list):
        raise Invalid('Usage sessions must be an array.')
    if not sessions:
        if usage['complete']: raise Invalid('No session evidence cannot establish complete zero cost.')
        return {'known_credits': 0.0, 'root_credits': 0.0, 'helper_credits': 0.0,
                'complete': False, 'session_count': 0, 'rate_card_sha256': digest(rates),
                'usage_sha256': digest(usage), 'billing_ledger': False}
    indexed = {}
    for s in sessions:
        sid = s.get('session_id')
        if not isinstance(sid, str) or not sid or sid in indexed:
            raise Invalid('Missing or duplicate native session identity.')
        if not isinstance(s.get('model'), str) or not isinstance(s.get('effort'), str):
            raise Invalid('Session route missing.')
        indexed[sid] = s
    roots = [s for s in sessions if s.get('parent_id') is None]
    if len(roots) != 1:
        raise Invalid('Exactly one root session is required.')
    total = Decimal(0); parent = Decimal(0); complete = usage['complete']
    for s in sessions:
        ancestors = {s['session_id']}; cursor = s.get('parent_id')
        while cursor is not None:
            if cursor not in indexed or cursor in ancestors:
                raise Invalid('Missing parent or cyclic native lineage.')
            ancestors.add(cursor); cursor = indexed[cursor].get('parent_id')
        values = rates.get('models', {}).get(s['model'])
        if not isinstance(values, list) or len(values) != 3:
            raise Invalid(f'Unknown rate for {s["model"]}; do not assume free usage.')
        tariffs = [Decimal(str(v)) for v in values]
        if any(not v.is_finite() or v < 0 for v in tariffs):
            raise Invalid('Rates must be finite and nonnegative.')
        tokens = s.get('tokens')
        if tokens is None:
            complete = False; continue
        keys = ('input_tokens', 'cached_input_tokens', 'output_tokens')
        if any(type(tokens.get(k)) is not int or tokens[k] < 0 for k in keys):
            raise Invalid('Token counts must be nonnegative integers.')
        if tokens['cached_input_tokens'] > tokens['input_tokens']:
            raise Invalid('Cached input is a subset, not extra input.')
        if 'reasoning_output_tokens' in tokens and (type(tokens['reasoning_output_tokens']) is not int or
                not 0 <= tokens['reasoning_output_tokens'] <= tokens['output_tokens']):
            raise Invalid('Reasoning tokens must be a subset of output.')
        counts = [tokens['input_tokens'] - tokens['cached_input_tokens'],
                  tokens['cached_input_tokens'], tokens['output_tokens']]
        cost = sum(Decimal(n) * rate for n, rate in zip(counts, tariffs)) / Decimal(1_000_000)
        total += cost
        if s.get('parent_id') is None: parent += cost
    return {'known_credits': float(total), 'root_credits': float(parent),
            'helper_credits': float(total - parent), 'complete': complete,
            'session_count': len(sessions), 'rate_card_sha256': digest(rates),
            'usage_sha256': digest(usage), 'billing_ledger': False}


def seal_record(record: dict) -> dict:
    record['record_sha256'] = digest({k:v for k,v in record.items() if k not in ('record_sha256','review')})
    return record


def make_record(doc: dict, run_id: str, grade: dict | None, usage: dict, rates: dict,
                termination: str, kind: str, invalid_reason: str | None = None) -> dict:
    verify_schedule(doc)
    run = next((r for r in doc['runs'] if r['run_id'] == run_id), None)
    if run is None: raise Invalid('Run is not in the frozen schedule.')
    if kind not in ('simulation', 'imported'):
        raise Invalid('Use an explicitly simulated or imported execution kind.')
    if termination not in ('completed', 'timeout', 'cancelled', 'infrastructure_error'):
        raise Invalid('Unknown termination reason.')
    if termination == 'infrastructure_error' and not invalid_reason:
        raise Invalid('Infrastructure failure needs an explicit adjudication reason.')
    if kind == 'imported':
        route_errors=[]
        for session in usage.get('sessions',[]):
            if session.get('parent_id') is None:
                if session.get('model') != run.get('root_model') or session.get('effort') != run.get('root_effort'):
                    route_errors.append('Root route is not frozen or does not match the schedule.')
            elif run.get('helpers_enabled') is not True:
                route_errors.append('Helper observed where capability is disabled or unresolved.')
            elif session.get('model') != run.get('helper_model') or session.get('effort') != run.get('helper_effort'):
                route_errors.append('Helper model/effort deviated from the frozen route.')
        if route_errors:
            invalid_reason=' '.join(([invalid_reason] if invalid_reason else [])+sorted(set(route_errors)))
    if grade is None:
        if not invalid_reason:
            raise Invalid('Missing independent grade requires explicit infrastructure adjudication.')
        return seal_record({**run, 'schedule_sha256': doc['schedule_sha256'], 'execution_kind': kind,
                'termination': termination, 'invalid_reason': invalid_reason,
                'grade_sha256': None, 'artifact_sha256': None, 'functional_pass': False,
                'delivery_pass': False, 'integrity_pass': False, 'cost': price_usage(usage, rates),
                'review': None, 'runtime_certified': False})
    for field, key in (('task_id', 'task_id'), ('task_sha256', 'task_sha256'),
                       ('evaluator_sha256', 'evaluator_sha256')):
        if grade.get(field) != run[key]: raise Invalid(f'Grade mismatch: {field}')
    if not isinstance(grade.get('artifact_sha256'), str) or len(grade['artifact_sha256']) != 64:
        raise Invalid('Artifact hash missing.')
    tests = grade.get('tests', [])
    if not tests or len({t['id'] for t in tests}) != len(tests):
        raise Invalid('Grade needs unique independent checks.')
    if any(type(t.get('passed')) is not bool or t.get('kind') not in ('feature', 'regression') for t in tests):
        raise Invalid('Invalid check status.')
    identities = sorted([{'id': t['id'], 'kind': t['kind']} for t in tests], key=lambda t: t['id'])
    if digest(identities) != run['checks_sha256']:
        raise Invalid('The grade omitted, added, or changed frozen evaluator checks.')
    if {t['kind'] for t in tests} != {'feature', 'regression'}:
        raise Invalid('Both feature and regression checks are required.')
    if type(grade.get('integrity_pass')) is not bool:
        raise Invalid('Integrity result missing.')
    if kind == 'imported' and grade.get('execution') != 'docker_untrusted':
        raise Invalid('Imported results require independently sandboxed grading, not local controls.')
    record = {**run, 'schedule_sha256': doc['schedule_sha256'], 'execution_kind': kind,
              'termination': termination, 'invalid_reason': invalid_reason,
              'grade_sha256': digest(grade), 'artifact_sha256': grade['artifact_sha256'],
              'functional_pass': all(t['passed'] for t in tests),
              'delivery_pass': True, 'integrity_pass': grade['integrity_pass'],
              'cost': price_usage(usage, rates), 'review': None,
              'runtime_certified': False, 'human_review_minutes': None, 'human_repair_minutes': None,
              'test_summary': [{'id': t['id'], 'kind': t['kind'], 'passed': t['passed']} for t in tests],
              'note': 'Independent artifact grading plus supplied usage; runtime efficacy is not certified.'}
    # Workspace submission is captured even at timeout. Do not conflate timeout with functional failure.
    return seal_record(record)


def acceptable(row: dict) -> bool | None:
    if row.get('invalid_reason'): return None
    if not all(row.get(k) is True for k in ('functional_pass', 'delivery_pass', 'integrity_pass')):
        return False
    review = row.get('review')
    if review is None: return None
    validate_review(review, row['artifact_sha256'])
    return not review['blocker'] and min(review['scores'].values()) >= 2


def validate_review(review: dict, artifact_hash: str) -> None:
    if review.get('artifact_sha256') != artifact_hash:
        raise Invalid('Review refers to a different artifact.')
    if review.get('reviewer_kind') != 'human' or not review.get('reviewer_id') or not review.get('evidence'):
        raise Invalid('Human reviewer identity and supporting evidence are required.')
    if type(review.get('blocker')) is not bool or set(review.get('scores', {})) != set(DIMENSIONS):
        raise Invalid('Review needs all rubric dimensions and an explicit blocker decision.')
    if any(type(v) is not int or not 0 <= v <= 3 for v in review['scores'].values()):
        raise Invalid('Rubric scores must be integers from 0 through 3.')


def review_packets(study: Path, out: Path, mapping_path: Path) -> dict:
    if out.exists() or mapping_path.exists() or out.resolve() == mapping_path.resolve() or out.resolve() in mapping_path.resolve().parents:
        raise Invalid('Use a new packet directory and a new mapping OUTSIDE that directory.')
    catalog = read_json(study / 'catalog.json'); mapping = {}
    out.mkdir(parents=True)
    for path in sorted((study / 'records').glob('*.json')):
        row = read_json(path)
        if row.get('invalid_reason') or not row['functional_pass'] or not row['integrity_pass']:
            continue
        task = lookup(catalog, row['task_id']); key = secrets.token_hex(12)
        submitted = snapshot(study / 'workspaces' / row['run_id'])
        if digest(submitted) != row['artifact_sha256']:
            raise Invalid('Workspace changed after grading; regenerate the grade, not its hash.')
        baseline = {**task['files'], **task['user_overlay']}
        diff = []
        for name in sorted(set(baseline) | set(submitted)):
            if name in ('TASK.md', 'AGENTS.md'): continue
            diff.extend(difflib.unified_diff(baseline.get(name, '').splitlines(True),
                                           submitted.get(name, '').splitlines(True),
                                           fromfile='before/' + name, tofile='after/' + name))
        packet = out / key; packet.mkdir()
        (packet / 'change.patch').write_text(''.join(diff), encoding='utf-8')
        (packet / 'task.md').write_text(task['task'], encoding='utf-8')
        write_new(packet / 'verification.json', {'checks':row.get('test_summary',[]),
                  'integrity_pass':row['integrity_pass'],
                  'handoff_note':'Agent handoff transcript is not captured here. Do not invent reporting-quality evidence.'})
        write_new(packet / 'review.json', {'artifact_sha256': row['artifact_sha256'],
                  'reviewer_kind': 'human', 'reviewer_id': None, 'evidence': None,
                  'blocker': None, 'scores': dict.fromkeys(DIMENSIONS)})
        mapping[key] = {'run_id': row['run_id'], 'artifact_sha256': row['artifact_sha256']}
    write_new(mapping_path, mapping)
    return {'packets': len(mapping), 'labels_removed': ['condition', 'model', 'usage', 'cost'],
            'note': 'Code can still indirectly reveal its style; direct labels are withheld.'}


def _percentile(values: list[float], p: float) -> float:
    ordered = sorted(values); x = (len(ordered) - 1) * p
    lower = math.floor(x); upper = math.ceil(x)
    return ordered[lower] * (upper - x) + ordered[upper] * (x - lower) if upper != lower else ordered[lower]


def paired_contrast(rows: list[dict], candidate: str, control: str, seed: int,
                    contrasts: int, resamples: int = 2000) -> dict:
    by_slot = {(r['task_id'], r['repeat'], r['condition']): r for r in rows}
    task_values = defaultdict(list); excluded = []
    slots = sorted({(r['task_id'], r['repeat']) for r in rows})
    for task, repeat in slots:
        a = by_slot.get((task, repeat, candidate)); b = by_slot.get((task, repeat, control))
        if not a or not b or any(r.get('invalid_reason') or not r['cost']['complete'] or acceptable(r) is None for r in (a, b)):
            excluded.append({'task_id': task, 'repeat': repeat}); continue
        if a['source_family'] != b['source_family']:
            raise Invalid('Paired source family mismatch.')
        task_values[task].append((a['cost']['known_credits'], int(acceptable(a)),
                                  b['cost']['known_credits'], int(acceptable(b)), a['source_family']))
    groups = defaultdict(list)
    for values in task_values.values():
        means = [sum(v[i] for v in values) / len(values) for i in range(4)]
        groups[values[0][4]].append(means)
    points = [v for group in groups.values() for v in group]
    result = {'candidate': candidate, 'control': control, 'paired_tasks': len(points),
              'source_groups': len(groups), 'excluded_slots': excluded,
              'analysis': 'exploratory paired source-cluster bootstrap; repeats averaged within task',
              'intervals': None}
    if not points: return result
    def measures(selected):
        n = len(selected)
        ac, ap, bc, bp = [sum(v[i] for v in selected) / n for i in range(4)]
        ratio = (ac / ap) / (bc / bp) if ap > 0 and bp > 0 and bc > 0 else None
        return ap - bp, ratio
    gap, ratio = measures(points)
    result.update({'acceptance_difference': gap, 'cost_per_acceptable_ratio': ratio})
    if len(groups) < 6:
        result['interval_note'] = 'Fewer than six independent source groups; intervals withheld.'
        return result
    rng = random.Random(seed); keys = sorted(groups); differences = []; ratios = []
    for _ in range(resamples):
        selected = [v for key in rng.choices(keys, k=len(keys)) for v in groups[key]]
        delta, cost_ratio = measures(selected); differences.append(delta); ratios.append(cost_ratio)
    tail = 0.05 / (2 * contrasts)
    result['intervals'] = {'familywise_target': 0.95, 'bonferroni_contrasts': contrasts,
                          'acceptance_difference': [_percentile(differences, tail), _percentile(differences, 1-tail)],
                          'cost_per_acceptable_ratio': None}
    if all(value is not None for value in ratios):
        result['intervals']['cost_per_acceptable_ratio'] = [_percentile(ratios, tail), _percentile(ratios, 1-tail)]
    else:
        result['ratio_note'] = 'Zero-success or zero-cost bootstrap draws make ratio bounds unavailable; no draws discarded.'
    return result


def summarize(doc: dict, rows: list[dict]) -> dict:
    verify_schedule(doc); slots = {r['run_id']: r for r in doc['runs']}; seen = set()
    for row in rows:
        if row.get('record_sha256') != digest({k:v for k,v in row.items() if k not in ('record_sha256','review')}):
            raise Invalid('Stored record changed; preserve the original instead of silently rewriting it.')
        if row['run_id'] in seen or row['run_id'] not in slots:
            raise Invalid('Duplicate or unscheduled result.')
        seen.add(row['run_id']); expected = slots[row['run_id']]
        if row['schedule_sha256'] != doc['schedule_sha256'] or any(row[k] != expected[k] for k in expected):
            raise Invalid('Record no longer matches frozen schedule.')
        if not math.isfinite(row['cost']['known_credits']) or row['cost']['known_credits'] < 0:
            raise Invalid('Invalid recorded credits.')
    kinds = {r['execution_kind'] for r in rows}
    if len(kinds) > 1: raise Invalid('Never pool simulated and imported outcomes.')
    rate_cards = {r['cost']['rate_card_sha256'] for r in rows}
    if len(rate_cards) > 1: raise Invalid('Normalize all records using the same frozen rate card.')
    arms = {}
    for condition in doc['conditions']:
        recorded = [r for r in rows if r['condition'] == condition]
        valid = [r for r in recorded if not r.get('invalid_reason')]
        reviews = [acceptable(r) for r in valid]
        complete = bool(valid) and all(r['cost']['complete'] for r in valid)
        cost = sum(r['cost']['known_credits'] for r in valid)
        # Equal task weights, even when repeat counts differ after exclusions.
        tasks = defaultdict(list)
        for r in valid: tasks[r['task_id']].append(r)
        task_cost = sum(sum(r['cost']['known_credits'] for r in rs)/len(rs) for rs in tasks.values())
        task_acceptance = sum(sum(acceptable(r) is True for r in rs)/len(rs) for rs in tasks.values())
        arms[condition] = {'recorded': len(recorded), 'valid': len(valid),
                           'invalid': len(recorded)-len(valid),
                           'functional_passes': sum(r['functional_pass'] for r in valid),
                           'acceptable_solutions': sum(v is True for v in reviews),
                           'pending_quality_reviews': sum(v is None for v in reviews),
                           'timeouts': sum(r['termination']=='timeout' for r in valid),
                           'known_workflow_credits': cost, 'cost_complete': complete,
                           'known_root_credits': sum(r['cost']['root_credits'] for r in valid),
                           'known_helper_credits': sum(r['cost']['helper_credits'] for r in valid),
                           'quality_complete': None not in reviews,
                           'cost_note': 'Recorded valid attempts only; incomplete usage is a lower bound.',
                           'known_infrastructure_credits': sum(r['cost']['known_credits'] for r in recorded if r.get('invalid_reason')),
                           'task_weighted_cost_per_acceptable': task_cost/task_acceptance
                           if complete and None not in reviews and task_acceptance else None}
    partial = len(rows) != len(slots)
    result = {'status': 'partial' if partial else 'complete_import', 'expected_attempts': len(slots),
              'recorded_attempts': len(rows), 'missing_run_ids': sorted(set(slots)-seen),
              'execution_kind': next(iter(kinds), 'no_results'), 'conditions': arms,
              'scope': 'Fixed synthetic development suite; not confirmation on real workloads.',
              'promotion': 'not_evaluated',
              'promotion_blockers': ['Native runtime controls and inference authorization are not certified by this offline tool.',
                                     'Quality thresholds and a confirmatory design need separate approval.'],
              'contrasts': []}
    if partial: result['promotion_blockers'].append('Scheduled outcomes are missing; no full-study conclusion.')
    if kinds == {'simulation'}:
        result['promotion_blockers'].append('Simulation verifies plumbing, not instruction efficacy.')
    elif rows and not partial:
        for candidate, control in doc['primary_contrasts']:
            result['contrasts'].append(paired_contrast(rows, candidate, control, doc['seed'], len(doc['primary_contrasts'])))
    return result


def markdown_report(result: dict) -> str:
    lines = ['# Development comparison report', '',
             f"Status: **{result['status']}**. Execution: **{result['execution_kind']}**.",
             f"Recorded {result['recorded_attempts']} of {result['expected_attempts']} scheduled attempts.",
             '', result['scope'], '',
             '| Condition | Valid | Functional passes | Accepted | Pending review | Known workflow credits | Cost/acceptable |',
             '|---|---:|---:|---:|---:|---:|---:|']
    for name, arm in result['conditions'].items():
        value=arm['task_weighted_cost_per_acceptable']
        cost='not established' if value is None else f'{value:.4f}'
        qualifier='' if arm['cost_complete'] else ' (incomplete)'
        lines.append(f"| {name} | {arm['valid']} | {arm['functional_passes']} | {arm['acceptable_solutions']} | {arm['pending_quality_reviews']} | {arm['known_workflow_credits']:.4f}{qualifier} | {cost} |")
    lines += ['', 'Credits include failed valid attempts; infrastructure expenditure is reported separately in JSON.',
              'Missing review is not acceptance; missing usage is not zero cost.', '', '## Promotion', '',
              '**Not evaluated.** This report cannot authorize inference or certify instruction efficacy.']
    lines += ['', *['- '+reason for reason in result['promotion_blockers']], '']
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    prep = sub.add_parser('prepare'); prep.add_argument('--catalog', type=Path, default=CATALOG)
    prep.add_argument('--protocol', type=Path, required=True); prep.add_argument('--tasks', default='smoke')
    prep.add_argument('--repeats', type=int, default=1); prep.add_argument('--seed', type=int, required=True)
    prep.add_argument('--out', type=Path, required=True)
    native = sub.add_parser('native-usage'); native.add_argument('--trial', type=Path, required=True)
    native.add_argument('--out', type=Path, required=True)
    record = sub.add_parser('record'); record.add_argument('--study', type=Path, required=True)
    record.add_argument('--run', required=True); record.add_argument('--grade', type=Path)
    record.add_argument('--usage', type=Path, required=True); record.add_argument('--rates', type=Path, required=True)
    record.add_argument('--kind', choices=['simulation','imported'], required=True)
    record.add_argument('--termination', choices=['completed','timeout','cancelled','infrastructure_error'], required=True)
    record.add_argument('--invalid-reason')
    packets = sub.add_parser('review-packets'); packets.add_argument('--study', type=Path, required=True)
    packets.add_argument('--out', type=Path, required=True); packets.add_argument('--mapping', type=Path, required=True)
    review = sub.add_parser('attach-review'); review.add_argument('--study', type=Path, required=True)
    review.add_argument('--mapping', type=Path, required=True); review.add_argument('--packet', required=True)
    review.add_argument('--review', type=Path, required=True)
    report = sub.add_parser('report'); report.add_argument('--study', type=Path, required=True)
    report.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'prepare':
            catalog = load_catalog(args.catalog)
            ids = catalog['smoke_task_ids'] if args.tasks == 'smoke' else args.tasks.split(',')
            result = prepare(catalog, read_json(args.protocol), ids, args.repeats, args.seed, args.out)
        elif args.command == 'native-usage':
            result = native_usage(args.trial); write_new(args.out, result)
        elif args.command == 'record':
            result = make_record(read_json(args.study/'schedule.json'), args.run, read_json(args.grade) if args.grade else None,
                                 read_json(args.usage), read_json(args.rates), args.termination,
                                 args.kind, args.invalid_reason)
            write_new(args.study/'records'/f'{args.run}.json', result)
        elif args.command == 'review-packets':
            result = review_packets(args.study, args.out, args.mapping)
        elif args.command == 'attach-review':
            match = read_json(args.mapping)[args.packet]; result = read_json(args.review)
            validate_review(result, match['artifact_sha256'])
            row = read_json(args.study/'records'/f'{match["run_id"]}.json')
            if row['artifact_sha256'] != match['artifact_sha256']: raise Invalid('Review mapping mismatch.')
            write_new(args.study/'reviews'/f'{match["run_id"]}.json', result)
        else:
            doc = read_json(args.study/'schedule.json'); rows=[]
            for path in sorted((args.study/'records').glob('*.json')):
                row=read_json(path); review=args.study/'reviews'/f'{row["run_id"]}.json'
                if review.exists(): row['review']=read_json(review)
                rows.append(row)
            result=summarize(doc, rows)
            md=args.out.with_suffix('.md')
            if args.out.suffix != '.json' or args.out.exists() or md.exists():
                raise Invalid('Choose new report.json and report.md paths; reports are never overwritten.')
            write_new(args.out,result)
            with md.open('x',encoding='utf-8') as stream:stream.write(markdown_report(result))
        print(json.dumps(result,indent=2,allow_nan=False)); return 0
    except (Invalid,OSError,ValueError,KeyError,TypeError,AssertionError) as exc:
        print(json.dumps({'status':'error','error':str(exc)}),file=sys.stderr);return 1


if __name__ == '__main__':
    raise SystemExit(main())
