"""Prepare/run fresh matched attempts outside this repository; never install globals."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import subprocess
import threading

PACKAGE = Path(__file__).resolve().parents[1]
REPOSITORY = PACKAGE.parents[1]

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf8')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check_sources(deep, pier_source):
    for key, root in [('deep-swe', deep), ('pier', pier_source)]:
        for name, digest in read(PACKAGE / 'upstream-index.json')[key].items():
            if sha(root / name) != digest:
                raise ValueError(f'Pinned source drift: {key}/{name}')

def check_images():
    for task, expected in read(PACKAGE / 'images.json').items():
        observed = json.loads(subprocess.check_output(['docker', 'image', 'inspect', expected['tag']], text=True))[0]
        if observed['Id'] != expected['id'] or observed['RepoDigests'] != expected['repo_digests']:
            raise ValueError(f'Image drift: {task}')

def external_workdir(path):
    path = path.resolve()
    if path == REPOSITORY or REPOSITORY in path.parents:
        raise ValueError('Replay work directory must be outside this repository; generated config contains a private auth-file path')
    return path

def prepare(args):
    work = external_workdir(args.work_dir)
    if work.exists():
        raise ValueError('Use a new, nonexistent work directory; evidence is never overwritten')
    deep, pier_source = args.deep.resolve(), args.pier_source.resolve()
    if any(p == work or work in p.parents or p in work.parents for p in (deep, pier_source)):
        raise ValueError('Work directory and pinned source directories must be separate')
    if not args.auth_file.resolve().is_file() or not args.pier.resolve().is_file():
        raise ValueError('Existing auth file and pinned-environment Pier executable are required')
    check_sources(deep, pier_source)
    check_images()
    work.mkdir(parents=True)
    configs = work / 'configs'
    configs.mkdir()
    mode = 'none' if args.arm == 'none' else 'globals'
    runtime = (PACKAGE / 'tools' / ('runtime_' + mode + '.py')).read_text(encoding='utf8')
    owner = 'deepswe-replay-' + args.arm + '-' + hashlib.sha256(str(work).encode()).hexdigest()[:12]
    runtime = runtime.replace('deepswe-calibration-v1' if mode == 'none' else 'deepswe-current-global-v1', owner)
    global_sha = None
    if mode == 'globals':
        runtime = runtime.replace("'current-global.md'", "'global.md'")
        source = PACKAGE / 'instructions' / (args.arm + '.md')
        (work / 'global.md').write_bytes(source.read_bytes())
        global_sha = sha(source)
    (work / 'global_codex.py').write_text(runtime, encoding='utf8', newline='\n')
    schedule = read(PACKAGE / 'schedule.json')
    for number, job in enumerate(schedule, 1):
        name = f'{args.arm}-{number:03}'
        job['attempt_id'] = name
        cfg = {'job_name': name, 'jobs_dir': str(work / 'runs'), 'n_attempts': 1,
            'n_concurrent_trials': 1, 'quiet': True, 'retry': {'max_retries': 0},
            'environment': {'import_path': 'global_codex:CalibrationDocker', 'delete': False},
            'agents': [{'import_path': 'global_codex:CleanCodex', 'model_name': 'openai/' + job['model'],
                'override_timeout_sec': 1200, 'kwargs': {'version': '0.154.0-alpha.6.2', 'reasoning_effort': job['effort']},
                'env': {'CODEX_AUTH_JSON_PATH': str(args.auth_file.resolve())}}],
            'tasks': [{'path': str(deep / 'tasks' / job['task'])}]}
        save(configs / (name + '.json'), cfg)
    fixed = {p.relative_to(work).as_posix(): sha(p) for p in work.rglob('*') if p.is_file()}
    save(work / 'manifest.json', {'state': 'prepared', 'arm': args.arm, 'owner_label': owner,
        'schedule': schedule, 'concurrency': 2, 'root_start_cap': 18, 'files': fixed,
        'global_sha256': global_sha, 'deep': str(deep), 'pier_source': str(pier_source),
        'pier': str(args.pier.resolve()), 'package_files': {p.relative_to(PACKAGE).as_posix(): sha(p)
            for p in PACKAGE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}})
    print(json.dumps({'state': 'prepared', 'attempts': 18, 'arm': args.arm, 'inference_started': False}))

def run(args):
    work = external_workdir(args.work_dir)
    manifest = read(work / 'manifest.json')
    if manifest['state'] != 'prepared':
        raise ValueError('Only a prepared, never-started arm can run; no automatic resume/retry')
    for name, digest in manifest['files'].items():
        if sha(work / name) != digest:
            raise ValueError('Frozen replay input drift: ' + name)
    for name, digest in manifest['package_files'].items():
        if sha(PACKAGE / name) != digest:
            raise ValueError('Benchmark package drift after preparation: ' + name)
    check_sources(Path(manifest['deep']), Path(manifest['pier_source']))
    check_images()
    manifest['state'] = 'running'
    save(work / 'manifest.json', manifest)
    stop = threading.Event()
    env = {**os.environ, 'PYTHONPATH': str(work), 'PYTHONUTF8': '1', 'PYTHONDONTWRITEBYTECODE': '1', 'NO_COLOR': '1'}
    for key in ('OPENAI_API_KEY', 'OPENAI_BASE_URL', 'OPENAI_API_BASE', 'CODEX_FORCE_AUTH_JSON'):
        env.pop(key, None)
    starts = work / 'starts'
    starts.mkdir()
    def one(job):
        if stop.is_set() or (work / 'PAUSE').exists():
            return
        name = job['attempt_id']
        with (starts / (name + '.json')).open('x', encoding='utf8') as stream:
            json.dump(job, stream)
        print('Starting ' + name, flush=True)
        with (work / 'configs' / (name + '.log')).open('w', encoding='utf8') as log:
            result = subprocess.run([manifest['pier'], 'run', '-c', str(work / 'configs' / (name + '.json'))],
                cwd=work, env=env, stdout=log, stderr=subprocess.STDOUT,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        paths = [p for p in (work / 'runs' / name).rglob('result.json') if p.parent != work / 'runs' / name]
        invalid = len(paths) != 1
        if not invalid:
            trial = read(paths[0])
            exception = (trial.get('exception_info') or {}).get('exception_type')
            invalid = exception not in (None, 'AgentTimeoutError') or not (paths[0].parent / 'verifier/reward.json').exists()
            invalid = invalid or not (paths[0].parent / 'agent/inference-started.json').exists()
            invalid = invalid or not bool((trial.get('agent_result') or {}).get('n_input_tokens'))
        if invalid:
            stop.set()
        save(work / 'configs' / (name + '.outcome.json'), {'invalid': invalid, 'returncode': result.returncode,
            'result_paths': [str(p) for p in paths]})
        print(json.dumps({'attempt': name, 'invalid': invalid}), flush=True)
    def guarded(job):
        try:
            return one(job)
        except Exception:
            stop.set()
            raise
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(guarded, job) for job in manifest['schedule']]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception:
                stop.set()
                raise
    manifest['state'] = 'needs_attention' if stop.is_set() or (work / 'PAUSE').exists() else 'completed'
    save(work / 'manifest.json', manifest)
    print(json.dumps({'state': manifest['state'], 'root_starts': len(list(starts.glob('*.json')))}))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('prepare')
    p.add_argument('--arm', choices=['none', 'previous', 'revised'], required=True)
    for flag in ('work-dir', 'deep', 'pier-source', 'pier', 'auth-file'):
        p.add_argument('--' + flag, type=Path, required=True)
    p = commands.add_parser('run')
    p.add_argument('--work-dir', type=Path, required=True)
    args = parser.parse_args()
    {'prepare': prepare, 'run': run}[args.command](args)

if __name__ == '__main__':
    main()
