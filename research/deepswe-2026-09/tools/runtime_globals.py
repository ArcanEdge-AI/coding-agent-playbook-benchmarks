"""Small Pier extension for a recorded, isolated current-global Codex arm.

The upstream tasks, oracle, verifier, and scoring are unchanged. This extension
only fixes the subject's configuration and checks it before model inference.
"""
import hashlib
import json
from pathlib import Path, PurePosixPath
import shlex
import time
from datetime import datetime, timezone

from pier.agents.installed.codex import Codex
from pier.agents.network import allowlist_from_urls
from pier.environments.docker.docker import DockerEnvironment

FLAGS = [
    'default_permissions="calibration"',
    'permissions.calibration.filesystem={":root"="read",":workspace_roots"={"."="write"},"/app/.git"="write","/tmp"="write","/root/.cache"="write","/opt/calibration/codex-home"="deny","/opt/calibration/codex-secrets"="deny","/logs"="deny","/tests"="deny","/solution"="deny"}',
    # Local sockets remain available for real application tests. Docker/Pier
    # restricts egress to the inference endpoints; the subject cannot browse.
    'permissions.calibration.network.enabled=true',
    'approval_policy="never"', 'features.multi_agent=false', 'features.apps=false',
    'features.remote_plugin=false', 'features.plugins=false', 'features.memories=false',
    'features.skill_search=false', 'features.skip_host_skill_discovery=true',
    'skills.include_instructions=false', 'skills.max_context_tokens=1',
    'features.browser_use=false', 'features.computer_use=false',
    'features.in_app_browser=false', 'features.image_generation=false',
    'features.view_image=false', 'features.hooks=false', 'web_search="disabled"',
    'features.shell_tool=true', 'features.unified_exec=true', 'analytics.enabled=false',
]
CONFIG_FLAGS = ' '.join('--config ' + shlex.quote(value) for value in FLAGS)
SHELL_INIT = 'if [ -s ~/.nvm/nvm.sh ]; then . ~/.nvm/nvm.sh; fi; '
PROBE = r'''import json,pathlib,socket,subprocess,urllib.request
out={}
for p in ('/opt/calibration/codex-secrets/probe-canary','/opt/calibration/codex-secrets/auth.json','/opt/calibration/codex-home/auth.json'):
 try:
  with open(p,'rb') as f:f.read(1)
  out[p]='READABLE'
 except OSError as e:out[p]=type(e).__name__
p=pathlib.Path('/app/.calibration-write-probe');p.write_text('ok');p.unlink();out['workspace_write']=True
def git(*args):
 return subprocess.check_output(['git',*args],cwd='/app',stderr=subprocess.STDOUT,text=True).strip()
base=git('rev-parse','HEAD');branch=git('branch','--show-current');status=git('status','--porcelain')
git('checkout','-b','calibration-git-write-probe')
p=pathlib.Path('/app/.calibration-git-probe');p.write_text('preflight only\n')
git('add','--',p.name)
git('-c','user.name=Calibration Preflight','-c','user.email=calibration@example.invalid','commit','--no-gpg-sign','-m','Temporary preflight commit')
commit=git('rev-parse','HEAD');assert commit!=base
git('checkout',branch)
git('update-ref','-d','refs/heads/calibration-git-write-probe',commit)
out['git_branch_commit']=git('rev-parse','HEAD')==base and git('status','--porcelain')==status and not p.exists()
out['git_base_sha']=base;out['git_start_branch']=branch
out['python_subprocess']=subprocess.run(['python3','-c','print(37)'],capture_output=True,text=True).stdout.strip()=='37'
out['node_subprocess']=subprocess.run(['node','-e',"const p=require('child_process').spawnSync('node',['-e','console.log(37)'],{encoding:'utf8'});process.stdout.write(p.stdout||'')"],capture_output=True,text=True).stdout.strip()=='37'
s=socket.socket();s.bind(('127.0.0.1',0));s.close();out['local_binding']=True
try:
 s=socket.create_connection(('1.1.1.1',443),timeout=2);s.close();out['direct_internet']='CONNECTED'
except OSError as e:out['direct_internet']=type(e).__name__
try:
 with urllib.request.urlopen('https://example.com',timeout=3) as r:r.read(1)
 out['proxy_internet']='CONNECTED'
except Exception as e:out['proxy_internet']=type(e).__name__
print(json.dumps(out))
'''


class CalibrationDocker(DockerEnvironment):
    def _prepare_egress_proxy_compose(self):
        super()._prepare_egress_proxy_compose()
        if self._egress_proxy_compose_path:
            script = self.trial_paths.trial_dir / 'egress-proxy/start-squid.sh'
            # Pier writes this Linux shell script with host-native CRLF on
            # Windows. Normalize the generated runtime file, not upstream data.
            script.write_bytes(script.read_bytes().replace(b'\r\n', b'\n'))

    def _write_resources_compose_file(self):
        path = super()._write_resources_compose_file()
        doc = json.loads(path.read_text(encoding='utf8'))
        main = doc['services']['main']
        main['security_opt'] = ['seccomp=unconfined']
        main['labels'] = {'codex.benchmark.owner': 'deepswe-current-global-v1'}
        path.write_text(json.dumps(doc), encoding='utf8')
        return path


class CleanCodex(Codex):
    _REMOTE_CODEX_HOME = PurePosixPath('/opt/calibration/codex-home')
    _REMOTE_CODEX_SECRETS_DIR = PurePosixPath('/opt/calibration/codex-secrets')
    def __init__(self, *args, probe_only=False, **kwargs):
        self.probe_only = probe_only
        super().__init__(*args, **kwargs)
        assert self._version == '0.154.0-alpha.6.2', self._version
        assert not self.skills_dir and not self.mcp_servers

    def network_allowlist(self):
        return allowlist_from_urls([], default_domains=['api.openai.com', 'chatgpt.com', 'auth.openai.com'])

    def build_cli_flags(self):
        return super().build_cli_flags() + ' ' + CONFIG_FLAGS

    async def exec_as_agent(self, environment, command, env=None, cwd=None, timeout_sec=None):
        marker = 'codex exec --dangerously-bypass-approvals-and-sandbox '
        if marker not in command:
            return await super().exec_as_agent(environment, command, env, cwd, timeout_sec)
        assert command.count(marker) == 1
        command = command.replace(marker, 'codex exec --ignore-user-config --color never --cd /app ', 1)
        run_args = (environment,)
        native = await super().exec_as_agent(*run_args, command=SHELL_INIT + 'codex --version', env=env, cwd='/app')
        assert native.stdout.strip() == 'codex-cli 0.154.0-alpha.6.2', native.stdout
        models = await super().exec_as_agent(*run_args, command=SHELL_INIT + 'codex debug models', env=env, cwd='/app')
        catalog = {row['slug']: row for row in json.loads(models.stdout)['models']}
        required = {'gpt-5.6-luna': {'medium', 'high', 'max'}, 'gpt-5.6-terra': {'high'},
                    'gpt-5.6-sol': {'high'}, 'gpt-6-astra': {'high'}}
        for model, efforts in required.items():
            assert efforts.issubset({row['effort'] for row in catalog[model]['supported_reasoning_levels']})
        (self.logs_dir / 'models.json').write_text(models.stdout, encoding='utf8')
        # The upstream prompt requires a branch from main, while two images
        # retain upstream's master name. Normalize only the name at the same SHA.
        branch_setup = r'''import json,subprocess
def git(*a):return subprocess.check_output(['git',*a],text=True).strip()
base=git('rev-parse','HEAD');before=git('branch','--show-current')
exists=subprocess.run(['git','show-ref','--verify','--quiet','refs/heads/main']).returncode==0
if exists:assert git('rev-parse','main')==base
else:git('branch','main',base)
git('checkout','main')
assert git('rev-parse','HEAD')==base
print(json.dumps({'original_branch':before,'subject_branch':'main','base_sha':base,'created_main':not exists}))
'''
        branch_result = await super().exec_as_agent(*run_args, command='python3 -c ' + shlex.quote(branch_setup), env=env, cwd='/app')
        assert branch_result.return_code == 0, branch_result.stderr
        (self.logs_dir / 'branch-setup.json').write_text(json.dumps(json.loads(branch_result.stdout.splitlines()[-1])), encoding='utf8')
        await super().exec_as_agent(*run_args, command="printf canary > /opt/calibration/codex-secrets/probe-canary", env=env)
        probe_cmd = SHELL_INIT + 'codex sandbox -P calibration ' + CONFIG_FLAGS + ' -C /app python3 -c ' + shlex.quote(PROBE)
        probe = await super().exec_as_agent(*run_args, command=probe_cmd, env=env, cwd='/app')
        assert probe.return_code == 0, probe.stderr
        report = json.loads(probe.stdout)
        (self.logs_dir / 'isolation.json').write_text(json.dumps(report, indent=2), encoding='utf8')
        assert all(report[p] in ('PermissionError', 'FileNotFoundError') for p in
                   ('/opt/calibration/codex-secrets/probe-canary', '/opt/calibration/codex-secrets/auth.json', '/opt/calibration/codex-home/auth.json')), report
        assert all(report[k] for k in ('workspace_write', 'git_branch_commit', 'python_subprocess', 'node_subprocess', 'local_binding')), report
        assert report['direct_internet'] != 'CONNECTED' and report['proxy_internet'] != 'CONNECTED', report
        # The sole context treatment: native discovery from container CODEX_HOME.
        frozen = Path(__file__).resolve().parent / 'current-global.md'
        global_bytes = frozen.read_bytes()
        global_sha = hashlib.sha256(global_bytes).hexdigest()
        await environment.upload_file(frozen, '/opt/calibration/codex-home/AGENTS.md')
        # Parse the exact upstream CLI invocation to recover its final task argument.
        tokens = shlex.split(command)
        instruction = tokens[tokens.index('--') + 1]
        debug = SHELL_INIT + 'codex debug prompt-input ' + self.build_cli_flags() + ' --config ' + shlex.quote('model="' + self.model_name.split('/')[-1] + '"') + ' ' + shlex.quote(instruction)
        startup = await super().exec_as_agent(*run_args, command=debug, env=env, cwd='/app')
        content = json.loads(startup.stdout)
        texts = [part.get('text', '') for msg in content for part in msg.get('content', [])]
        combined = '\n'.join(texts)
        assert texts[-1] == instruction
        for marker in ('<skills_instructions>', '<memory'):
            assert marker.lower() not in combined.lower(), marker
        normalized = combined.replace('\r\n', '\n')
        global_text = global_bytes.decode('utf8').replace('\r\n', '\n').strip()
        assert normalized.count(global_text) == 1, 'Global text missing, truncated or duplicated'
        assert normalized.count('coding-agent-playbook-codex:start') == 1
        (self.logs_dir / 'startup-input.json').write_text(startup.stdout, encoding='utf8')
        # Only the frozen global is present; repository instructions remain native.
        context_check = await super().exec_as_agent(*run_args,
            command="python3 -c " + shlex.quote("import json,pathlib; print(json.dumps({str(p):p.exists() for p in [pathlib.Path.home()/'AGENTS.md',pathlib.Path.home()/'.codex/AGENTS.md',pathlib.Path('/opt/calibration/codex-home/AGENTS.md'),pathlib.Path('/opt/calibration/codex-home/AGENTS.override.md')]}))"),
            env=env, cwd='/app')
        observed = json.loads(context_check.stdout)
        assert [p for p, exists in observed.items() if exists] == ['/opt/calibration/codex-home/AGENTS.md'], observed
        (self.logs_dir / 'preflight.json').write_text(json.dumps({'status': 'passed', 'model': self.model_name,
            'native_version': native.stdout.strip(), 'globals_absent': False, 'global_sha256': global_sha, 'global_present_exactly_once': True, 'helpers': 0,
            'startup_sha256': hashlib.sha256(startup.stdout.encode()).hexdigest(),
            'config_flags': FLAGS, 'instruction_sha256': hashlib.sha256(instruction.encode()).hexdigest(),
            'repo_instructions_retained': True, 'probe_only': self.probe_only}, indent=2), encoding='utf8')
        if self.probe_only:
            return await super().exec_as_agent(*run_args, command='true', env=env)
        started = time.monotonic()
        timing = {'started_at': datetime.now(timezone.utc).isoformat(), 'model': self.model_name}
        (self.logs_dir / 'inference-started.json').write_text(json.dumps(timing), encoding='utf8')
        try:
            return await super().exec_as_agent(*run_args, command='set -o pipefail; ' + command,
                                               env=env, cwd='/app', timeout_sec=timeout_sec)
        finally:
            timing.update({'finished_at': datetime.now(timezone.utc).isoformat(),
                           'seconds': time.monotonic() - started})
            (self.logs_dir / 'inference-timing.json').write_text(json.dumps(timing), encoding='utf8')
            # Diagnostic evidence only. Pier still grades only committed code.
            status = await super().exec_as_agent(*run_args,
                command='git status --short --branch; git log -3 --oneline', env=env, cwd='/app', timeout_sec=10)
            (self.logs_dir / 'submission-status.txt').write_text(status.stdout, encoding='utf8')
