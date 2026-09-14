"""Validate v1 planning metadata only; never run agents or certify readiness."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROTOCOLS = ('initial-globals-delegation', 'candidate-vs-incumbent')


def _integer(value: object) -> bool:
    return type(value) is int and value > 0


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_manifest(document: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ['Manifest must be an object.']
    if type(document.get('schema_version')) is not int or document['schema_version'] != 1:
        errors.append('Unsupported manifest schema_version.')
    if document.get('suite_id') != 'arcanedge-coding-v1':
        errors.append('Unexpected suite_id.')
    if document.get('status') != 'planning' or document.get('ready_for_scored_execution') is not False:
        errors.append('This catalog must remain explicitly planning-only.')
    targets = document.get('split_targets')
    if targets != {'development': 12, 'confirmation': 12, 'smoke_subset': 4}:
        errors.append('Expected the v1 12/12 targets and four-task smoke subset.')
    tasks = document.get('tasks')
    if not isinstance(tasks, list):
        return errors + ['tasks must be an array.']
    if len(tasks) != 24:
        errors.append('The v1 backlog must contain 24 proposed scenarios.')
    indexed: dict[str, dict] = {}
    source_splits: dict[str, set[str]] = {}
    for task in tasks:
        if not isinstance(task, dict):
            errors.append('Each task must be an object.')
            continue
        task_id = task.get('id')
        if not _text(task_id):
            errors.append('Each task needs an ID.')
            continue
        if task_id in indexed:
            errors.append(f'Duplicate task ID: {task_id}')
        indexed[task_id] = task
        for field in ('family', 'scenario', 'acceptance_evidence'):
            if not _text(task.get(field)):
                errors.append(f'{task_id}: missing {field}.')
        if task.get('status') != 'proposed':
            errors.append(f'{task_id}: this validator supports proposed scenarios only.')
        split = task.get('split')
        if split not in ('unassigned', 'development', 'confirmation'):
            errors.append(f'{task_id}: invalid split.')
        source = task.get('source_family')
        package = task.get('package_ref')
        if source is not None and not _text(source):
            errors.append(f'{task_id}: source_family must be null or nonempty text.')
        if package is not None and not _text(package):
            errors.append(f'{task_id}: package_ref must be null or nonempty text.')
        if split in ('development', 'confirmation'):
            if not _text(source) or not _text(package):
                errors.append(f'{task_id}: assigned split requires source_family and package_ref.')
            elif isinstance(source, str):
                source_splits.setdefault(source, set()).add(split)
    for source, splits in source_splits.items():
        if len(splits) > 1:
            errors.append(f'Source family crosses development/confirmation: {source}')
    for split in ('development', 'confirmation'):
        if sum(task.get('split') == split for task in indexed.values()) > 12:
            errors.append(f'Too many {split} assignments for the v1 target.')
    smoke = document.get('smoke_task_ids')
    if not isinstance(smoke, list) or any(not _text(item) for item in smoke):
        errors.append('smoke_task_ids must be an array of IDs.')
    else:
        if len(smoke) > 4 or len(set(smoke)) != len(smoke):
            errors.append('Smoke subset must have at most four unique tasks.')
        for task_id in smoke:
            if task_id not in indexed or indexed[task_id].get('split') != 'development':
                errors.append(f'Smoke task must belong to development: {task_id}')
    return errors


def validate_protocol(document: object) -> list[str]:
    if not isinstance(document, dict):
        return ['Protocol must be an object.']
    errors: list[str] = []
    if type(document.get('schema_version')) is not int or document['schema_version'] != 1:
        errors.append('Unsupported protocol schema_version.')
    if document.get('suite_id') != 'arcanedge-coding-v1':
        errors.append('Unexpected protocol suite_id.')
    if document.get('status') != 'draft':
        errors.append('Planning protocols must remain draft.')
    for field in ('inference_authorized', 'ready_for_scored_execution'):
        if document.get(field) is not False:
            errors.append(f'{field} must be false in a planning template.')
    runtime = document.get('runtime')
    if not isinstance(runtime, dict) or runtime.get('validated') is not False:
        errors.append('A planning template cannot claim runtime validation.')
    budget = document.get('budget')
    budget_fields = ('approved_total_credits', 'in_flight_reserve_credits', 'max_author_attempts', 'authorization_ref')
    if not isinstance(budget, dict) or any(field not in budget or budget[field] is not None for field in budget_fields):
        errors.append('Planning budgets must be explicitly unresolved, not approved.')
    kind = document.get('comparison_kind')
    if kind == 'globals_and_delegation':
        expected_id = PROTOCOLS[0]
        expected = [('A', 'none', True, 'shared'), ('B', 'non_delegation', False, None), ('C', 'full', True, 'shared')]
        contrasts = [['C', 'A'], ['C', 'B']]
    elif kind == 'instruction_revision':
        expected_id = PROTOCOLS[1]
        expected = [('incumbent', 'incumbent', None, 'freeze_identically'), ('candidate', 'candidate', None, 'freeze_identically')]
        contrasts = [['candidate', 'incumbent']]
    else:
        return errors + ['Unsupported comparison_kind.']
    if document.get('protocol_id') != expected_id:
        errors.append('Protocol ID does not match its comparison kind.')
    conditions = document.get('conditions')
    if not isinstance(conditions, list) or len(conditions) != len(expected):
        return errors + ['Incorrect condition count.']
    for condition, (name, globals_name, enabled, route) in zip(conditions, expected):
        if not isinstance(condition, dict):
            errors.append('Each condition must be an object.')
            continue
        if (condition.get('id'), condition.get('globals'), condition.get('helper_route')) != (name, globals_name, route):
            errors.append(f'Condition {name} violates the defined comparison.')
        if 'helpers_enabled' not in condition or condition['helpers_enabled'] is not enabled:
            errors.append(f'Condition {name} has an incorrect capability setting.')
    if document.get('primary_contrasts') != contrasts:
        errors.append('Primary contrasts do not match the defined causal questions.')
    stages = document.get('stages')
    if not isinstance(stages, list) or not stages:
        return errors + ['At least one illustrative stage is required.']
    expected_ids = [row[0] for row in expected]
    stage_ids: set[str] = set()
    for stage in stages:
        if not isinstance(stage, dict):
            errors.append('Each stage must be an object.')
            continue
        name = stage.get('id')
        if not _text(name) or name in stage_ids:
            errors.append('Stage IDs must be unique nonempty strings.')
        else:
            stage_ids.add(name)
        if stage.get('task_split') not in ('development', 'confirmation'):
            errors.append(f'{name}: invalid task split.')
        if stage.get('condition_ids') != expected_ids:
            errors.append(f'{name}: conditions must match the complete comparison.')
        if not all(_integer(stage.get(field)) for field in ('task_count', 'repeats', 'author_attempts')):
            errors.append(f'{name}: counts must be positive integers, not booleans.')
        elif stage['author_attempts'] != stage['task_count'] * stage['repeats'] * len(expected_ids):
            errors.append(f'{name}: incorrect author-attempt arithmetic.')
    return errors


def _unique_keys(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def check_repository(root: Path) -> list[str]:
    checks = [('benchmarks/v1/manifest.json', validate_manifest)]
    checks.extend((f'protocols/{name}.json', validate_protocol) for name in PROTOCOLS)
    errors: list[str] = []
    for relative, validator in checks:
        try:
            document = json.loads((root / relative).read_text(encoding='utf-8'), object_pairs_hook=_unique_keys)
            errors.extend(f'{relative}: {message}' for message in validator(document))
        except (OSError, ValueError) as exc:
            errors.append(f'{relative}: {exc}')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT, help='Repository root; defaults to this checkout.')
    args = parser.parse_args()
    errors = check_repository(args.root)
    print(json.dumps({'status': 'invalid' if errors else 'planning_metadata_valid',
                      'ready_for_scored_execution': False, 'inference_authorized': False,
                      'scope': 'Structural planning checks only; no task, runtime, or billing validation.',
                      'errors': errors}, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
