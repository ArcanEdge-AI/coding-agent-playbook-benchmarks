"""Materialize development repositories and independently grade their artifacts.

No command invokes a model. Untrusted submissions require a pinned Docker image.
Local control validation executes only content bound by the catalog's hashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / 'benchmarks/v1/tasks/development.json'
LANGUAGES = {'python', 'typescript', 'go'}
MAX_FILE_BYTES = 2_000_000
MAX_TOTAL_BYTES = 20_000_000


class Invalid(ValueError):
    """Missing, inconsistent, or unsafe evaluation inputs."""


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode('utf-8')


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Invalid(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=_pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(Invalid(value)))


def write_new(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write('\n')


def relative(name: str) -> Path:
    if not isinstance(name, str) or not name or '\\' in name or ':' in name:
        raise Invalid(f'Unsafe relative path: {name!r}')
    p = PurePosixPath(name)
    if p.is_absolute() or any(part in ('.', '..', '.git') for part in name.split('/')):
        raise Invalid(f'Unsafe relative path: {name!r}')
    if any(not part for part in name.split('/')):
        raise Invalid(f'Unsafe relative path: {name!r}')
    return Path(*p.parts)


def validate_task(task: dict) -> None:
    if task.get('split') != 'development' or task.get('language') not in LANGUAGES:
        raise Invalid('This catalog supports development tasks only.')
    if not re.fullmatch(r'[A-Z]+-\d{2}', task.get('id', '')):
        raise Invalid('Invalid task ID.')
    payload = {k: v for k, v in task.items() if k != 'package_sha256'}
    if task.get('package_sha256') != digest(payload):
        raise Invalid(f"Task content changed without a new identity: {task['id']}")
    if not re.fullmatch(r'[0-9a-f]{64}', task.get('evaluator_sha256', '')):
        raise Invalid('Evaluator identity missing.')
    if not task.get('files') or not isinstance(task.get('task'), str):
        raise Invalid('Task needs source files and a visible specification.')
    for group in ('files', 'user_overlay'):
        for name, content in task[group].items():
            relative(name)
            if not isinstance(content, str) or len(content.encode()) > MAX_FILE_BYTES:
                raise Invalid('Invalid source file content.')


def load_catalog(path: Path = CATALOG) -> dict:
    catalog = read_json(path)
    if catalog.get('schema_version') != 1 or catalog.get('inference_authorized') is not False:
        raise Invalid('Unsupported or incorrectly authorized catalog.')
    indexed = {}
    for task in catalog.get('tasks', []):
        validate_task(task)
        if task['id'] in indexed:
            raise Invalid('Duplicate task ID.')
        indexed[task['id']] = task
    smoke = catalog.get('smoke_task_ids', [])
    if not indexed or len(set(smoke)) != len(smoke) or not set(smoke) <= indexed.keys():
        raise Invalid('Invalid smoke selection.')
    return catalog


def lookup(catalog: dict, task_id: str) -> dict:
    for task in catalog['tasks']:
        if task['id'] == task_id:
            return task
    raise Invalid(f'Unknown task: {task_id}')


def put_files(root: Path, files: dict) -> None:
    for name, content in files.items():
        path = root / relative(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8', newline='\n')


def command(argv: list[str], cwd: Path, timeout: int = 30, stdin: str | None = None,
            env_extra: dict | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env.update({'PYTHONDONTWRITEBYTECODE': '1', 'GOTOOLCHAIN': 'local',
                'GOPROXY': 'off', 'GOSUMDB': 'off', 'GOWORK': 'off',
                'GORACE': 'atexit_sleep_ms=0 halt_on_error=1'})
    env.update(env_extra or {})
    try:
        process = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, env=env,
                                   start_new_session=(os.name != 'nt'))
    except FileNotFoundError as exc:
        raise Invalid(f'Required runtime unavailable: {argv[0]}') from exc
    try:
        stdout, stderr = process.communicate(input=stdin, timeout=timeout)
        return subprocess.CompletedProcess(argv, process.returncode, stdout, stderr)
    except subprocess.TimeoutExpired:
        if os.name != 'nt':
            try: os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError: pass
        else:
            process.kill()  # Untrusted execution uses Docker, removed separately below.
        process.communicate()
        return subprocess.CompletedProcess(argv, 124, '', f'Timeout after {timeout}s')


def materialize(task: dict, target: Path, init_git: bool = True) -> None:
    validate_task(task)
    target = target.resolve()
    if target == ROOT or ROOT in target.parents:
        raise Invalid('Subject workspaces must be outside the benchmark repository.')
    target.mkdir(parents=True, exist_ok=False)
    put_files(target, task['files'])
    put_files(target, {'TASK.md': task['task'] + '\n',
                      'AGENTS.md': 'This is an isolated development fixture. Follow TASK.md. '
                                   'Use only the local runtimes and standard libraries. '
                                   'No network or new dependencies. Preserve unrelated user work.\n'})
    if init_git:
        git_env = {'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
                   'GIT_AUTHOR_DATE': '2000-01-01T00:00:00Z',
                   'GIT_COMMITTER_DATE': '2000-01-01T00:00:00Z'}
        commands = [['git', 'init', '-q', '-b', 'main'], ['git', 'add', '--', '.'],
                    ['git', '-c', 'user.name=ArcanEdge Benchmark',
                     '-c', 'user.email=benchmark@example.invalid', '-c', 'commit.gpgsign=false',
                     '-c', f'core.hooksPath={os.devnull}', 'commit', '-qm', 'Pinned fixture baseline']]
        for argv in commands:
            result = command(argv, target, env_extra=git_env)
            if result.returncode:
                raise Invalid('Unable to initialize disposable fixture Git repository: ' + result.stderr)
    # Deliberately after the baseline commit: these are pre-existing untracked edits.
    put_files(target, task['user_overlay'])


def snapshot(root: Path) -> dict[str, str]:
    if not root.is_dir():
        raise Invalid('Workspace does not exist.')
    files = {}; total = 0
    for path in sorted(root.rglob('*')):
        rel = path.relative_to(root)
        if any(part in ('.git', '__pycache__') for part in rel.parts):
            continue
        if path.is_symlink():
            raise Invalid(f'Symlink not allowed in artifact: {rel}')
        if not path.is_file():
            continue
        size = path.stat().st_size
        total += size
        if size > MAX_FILE_BYTES or total > MAX_TOTAL_BYTES:
            raise Invalid('Workspace exceeds artifact size limits; remove build outputs.')
        try:
            files[rel.as_posix()] = path.read_text(encoding='utf-8')
        except UnicodeError as exc:
            raise Invalid(f'Non-text artifact: {rel}') from exc
    return files


def evaluator(task: dict, bundle: dict) -> dict:
    data = bundle.get('tasks', {}).get(task['id'])
    if not isinstance(data, dict) or digest(data) != task['evaluator_sha256']:
        raise Invalid('Missing evaluator or evaluator checksum mismatch.')
    return data


def _program(task: dict, workspace: Path, scratch: Path) -> tuple[list[str], str | None]:
    if task['language'] == 'python':
        return [sys.executable, '-S', '-B', 'app.py'], None
    if task['language'] == 'typescript':
        return ['node', '--experimental-strip-types', 'main.ts'], None
    binary = scratch / ('fixture.exe' if os.name == 'nt' else 'fixture')
    flags = ['go', 'build']
    if task['id'] == 'STATE-01':
        flags.append('-race')
    build = command(flags + ['-o', str(binary), '.'], workspace, timeout=120)
    return [str(binary)], None if build.returncode == 0 else build.stderr[-8000:]


def _unit_result(workspace: Path) -> dict:
    result = command([sys.executable, '-S', '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-v'], workspace)
    log = result.stdout + result.stderr
    count = re.search(r'Ran (\d+) tests?', log)
    return {'exit_code': result.returncode, 'collected': int(count.group(1)) if count else 0,
            'log': log[-8000:], 'test_failure': result.returncode == 1 and 'FAILED (' in log}


def observe(task: dict, files: dict, inputs: list, mode: str) -> dict:
    """Candidate-side worker: receives inputs, NEVER expected answers or references."""
    with tempfile.TemporaryDirectory(prefix='ae-worker-') as td:
        scratch = Path(td); workspace = scratch / 'workspace'; workspace.mkdir()
        put_files(workspace, files)
        if mode == 'mutation':
            return _unit_result(workspace)
        argv, error = _program(task, workspace, scratch)
        outputs = []
        for value in inputs:
            if error is not None:
                outputs.append({'exit_code': 1, 'stdout': '', 'stderr': error})
            else:
                run = command(argv, workspace, stdin=json.dumps(value))
                outputs.append({'exit_code': run.returncode, 'stdout': run.stdout[:MAX_FILE_BYTES],
                                'stderr': run.stderr[-4000:]})
        return {'outputs': outputs}


def sandbox_observe(task: dict, files: dict, inputs: list, mode: str, image: str) -> dict:
    if not re.fullmatch(r'[A-Za-z0-9./:_-]+@sha256:[0-9a-f]{64}', image):
        raise Invalid('Use an existing local grader image pinned by sha256 digest.')
    if shutil.which('docker') is None:
        raise Invalid('Docker is required to grade an untrusted artifact; no local fallback.')
    name = 'arcanedge-grade-' + uuid.uuid4().hex
    with tempfile.TemporaryDirectory(prefix='ae-input-') as td:
        stage = Path(td); stage.chmod(0o755)
        # The evaluator and its expected values remain in the host controller.
        request = {'task': {'id': task['id'], 'language': task['language']},
                   'files': files, 'inputs': inputs, 'mode': mode}
        write_new(stage / 'request.json', request); (stage / 'request.json').chmod(0o644)
        argv = ['docker', 'run', '--pull=never', '--name', name, '--init', '--network=none',
                '--read-only', '--cap-drop=ALL', '--security-opt=no-new-privileges',
                '--pids-limit=128', '--memory=1g', '--cpus=1', '--user=65534:65534',
                '--tmpfs=/tmp:rw,nosuid,size=536870912', '-e', 'HOME=/tmp',
                '-e', 'GOCACHE=/tmp/go-cache', '-e', 'CGO_ENABLED=1',
                '--mount', f'type=bind,src={stage},dst=/inputs,readonly',
                '--mount', f'type=bind,src={Path(__file__).resolve()},dst=/opt/arcanedge/tools/benchmark/suite.py,readonly',
                '--entrypoint', 'python3', image, '-S', '-B', '/opt/arcanedge/tools/benchmark/suite.py', '_observe']
        try:
            result = command(argv, stage, timeout=300)
            if result.returncode:
                raise Invalid(f'Sandbox grading failed ({result.returncode}): {result.stderr[-4000:]}')
            return json.loads(result.stdout)
        finally:
            command(['docker', 'rm', '-f', name], stage)


def grade_files(task: dict, data: dict, files: dict[str, str], image: str | None = None) -> dict:
    """Controller: use image for untrusted code; None is for frozen local controls only."""
    integrity = all(files.get(name) == value for name, value in task['user_overlay'].items())
    results = []
    def run(candidate, inputs, mode):
        if image is not None:
            return sandbox_observe(task, candidate, inputs, mode, image)
        return observe(task, candidate, inputs, mode)
    if data['kind'] == 'mutation':
        integrity &= all(files.get(k) == v for k, v in task['files'].items() if not k.startswith('tests/'))
        integrity &= all(k.startswith('tests/') or k in task['files'] or k in ('TASK.md', 'AGENTS.md') for k in files)
        correct = run(files, [], 'mutation')
        results.append({'id': 'correct-implementation', 'kind': 'regression',
                        'passed': correct['exit_code'] == 0 and correct['collected'] > 0, 'detail': correct})
        for mutant in data['mutants']:
            observed = run({**files, **mutant['files']}, [], 'mutation')
            results.append({'id': mutant['name'], 'kind': 'feature',
                            'passed': observed['test_failure'] and observed['collected'] > 0,
                            'detail': observed})
    else:
        observed = run(files, [t['input'] for t in data['tests']], 'io')
        if len(observed['outputs']) != len(data['tests']):
            raise Invalid('Candidate worker returned an inconsistent result count.')
        for test, output in zip(data['tests'], observed['outputs']):
            passed = False
            try:
                actual = json.loads(output['stdout'])
                passed = output['exit_code'] == 0 and canonical(actual) == canonical(test['expected'])
                detail = {'actual': actual, 'exit_code': output['exit_code']}
            except ValueError:
                detail = {'exit_code': output['exit_code'], 'stderr': output['stderr'][-4000:],
                          'stdout': output['stdout'][-4000:]}
            results.append({'id': test['id'], 'kind': test['kind'], 'passed': passed, 'detail': detail})
    feature = [r for r in results if r['kind'] == 'feature']
    regression = [r for r in results if r['kind'] == 'regression']
    return {'schema_version': 1, 'task_id': task['id'], 'task_sha256': task['package_sha256'],
            'evaluator_sha256': task['evaluator_sha256'], 'artifact_sha256': digest(files),
            'feature_pass': bool(feature) and all(r['passed'] for r in feature),
            'regression_pass': bool(regression) and all(r['passed'] for r in regression),
            'integrity_pass': bool(integrity), 'tests': results,
            'functional_pass': bool(feature) and bool(regression) and all(r['passed'] for r in results),
            'quality_review': None, 'acceptable': None,
            'execution': 'docker_untrusted' if image else 'trusted_local_control'}


def controls(catalog: dict, bundle: dict) -> dict:
    records = []
    for task in catalog['tasks']:
        data = evaluator(task, bundle)
        base = {**task['files'], **task['user_overlay']}
        variants = [('noop', base, False),
                    ('reference', {**base, **data['reference_files']}, True),
                    ('alternative', {**base, **data['alternative_files']}, True)]
        if data['kind'] != 'mutation':
            variants += [(m['name'], {**base, **m['files']}, False) for m in data['mutants']]
        for name, files, expected in variants:
            observed = grade_files(task, data, files)
            passed = observed['functional_pass'] and observed['integrity_pass']
            ok = passed == expected and observed['regression_pass']
            records.append({'task_id': task['id'], 'control': name, 'expected_functional_pass': expected,
                            'functional_pass': passed, 'regression_pass': observed['regression_pass'],
                            'control_passed': ok, 'checks': len(observed['tests'])})
            if not ok:
                raise Invalid(f'Control failed for {task["id"]}/{name}: {json.dumps(observed)}')
    return {'schema_version': 1, 'status': 'local_controls_passed', 'catalog_sha256': digest(catalog),
            'evaluator_bundle_sha256': digest(bundle), 'task_count': len(catalog['tasks']),
            'control_count': len(records), 'controls': records, 'model_calls': 0,
            'runtime_isolation_validated': False, 'inference_authorized': False,
            'scope': 'Trusted local reference/no-op/alternative/mutant controls; not agent outcomes.'}


def docker_grade(task: dict, bundle_path: Path, workspace: Path, image: str) -> dict:
    files = snapshot(workspace)
    data = evaluator(task, read_json(bundle_path))
    return grade_files(task, data, files, image=image)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', type=Path, default=CATALOG)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('validate')
    export = sub.add_parser('export'); export.add_argument('--task', required=True)
    export.add_argument('--out', type=Path, required=True)
    control = sub.add_parser('controls'); control.add_argument('--bundle', type=Path, required=True)
    control.add_argument('--out', type=Path, required=True)
    control.add_argument('--trusted-local-controls', action='store_true', required=True)
    grade = sub.add_parser('grade'); grade.add_argument('--task', required=True)
    grade.add_argument('--workspace', type=Path, required=True); grade.add_argument('--bundle', type=Path, required=True)
    grade.add_argument('--image', required=True); grade.add_argument('--out', type=Path, required=True)
    sub.add_parser('_observe', help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        if args.command == '_observe':
            request = read_json(Path('/inputs/request.json'))
            result = observe(request['task'], request['files'], request['inputs'], request['mode'])
        else:
            catalog = load_catalog(args.catalog)
            if args.command == 'validate':
                result = {'status': 'development_catalog_valid', 'tasks': len(catalog['tasks']),
                          'inference_authorized': False, 'runtime_isolation_validated': False}
            elif args.command == 'export':
                task = lookup(catalog, args.task); materialize(task, args.out)
                result = {'status': 'workspace_exported', 'task_id': args.task,
                          'path': str(args.out.resolve()), 'task_sha256': task['package_sha256']}
            elif args.command == 'controls':
                result = controls(catalog, read_json(args.bundle)); write_new(args.out, result)
            else:
                result = docker_grade(lookup(catalog, args.task), args.bundle, args.workspace, args.image)
                write_new(args.out, result)
        print(json.dumps(result, indent=2, allow_nan=False)); return 0
    except (Invalid, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'status': 'error', 'error': str(exc)}), file=sys.stderr); return 1


if __name__ == '__main__':
    raise SystemExit(main())
