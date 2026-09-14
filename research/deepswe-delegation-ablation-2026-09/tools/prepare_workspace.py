"""Prepare an external draft workspace only; never start model inference."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

PACKAGE=Path(__file__).resolve().parents[1]
COMPLETED=PACKAGE.parent/'deepswe-2026-09'
REPO=PACKAGE.parents[1]

def prepare(args):
    work=args.work_dir.resolve()
    if work.exists():raise ValueError('Choose a new directory; existing evidence is never overwritten')
    if work==REPO or REPO in work.parents:raise ValueError('The work directory must be outside the benchmark repository')
    paths={k:getattr(args,k).resolve() for k in ['deep','pier_source','pier','auth_file']}
    if not all(p.exists() for p in paths.values()):raise ValueError('Pinned source directories, Pier executable and external auth file must already exist')
    for p in paths.values():
        if p==work or work in p.parents or (p.is_dir() and p in work.parents):raise ValueError('Keep work, source and auth locations separate')
    work.mkdir(parents=True)
    for name in ['current.md','without-subagents.md']:
        (work/'instructions').mkdir(exist_ok=True);shutil.copyfile(PACKAGE/'instructions'/name,work/'instructions'/name)
    for name in ['controlled_codex.py','runtime.patch','instruction-edits.json','instructions.patch']:
        shutil.copyfile(PACKAGE/name,work/name)
    owner='deepswe-delegation-'+hashlib.sha256(str(work).encode()).hexdigest()[:12]
    runtime=(work/'controlled_codex.py').read_text(encoding='utf8')
    assert runtime.count("'deepswe-delegation-ablation-v1'")==1
    (work/'controlled_codex.py').write_text(runtime.replace("'deepswe-delegation-ablation-v1'",repr(owner)),encoding='utf8')
    shutil.copyfile(PACKAGE/'proposed-protocol.md',work/'PLAN.md')
    shutil.copyfile(COMPLETED/'credit-rates.json',work/'credit-rates.json')
    for p in (PACKAGE/'draft').glob('*.py'):shutil.copyfile(p,work/p.name)
    settings={k:str(v) for k,v in paths.items()};settings['completed_package']=str(COMPLETED)
    (work/'workspace-settings.json').write_text(json.dumps(settings,indent=2)+'\n',encoding='utf8')
    protected=['instructions/current.md','instructions/without-subagents.md','instruction-edits.json','credit-rates.json']
    (work/'preservation.json').write_text(json.dumps({'files':{n:hashlib.sha256((work/n).read_bytes()).hexdigest() for n in protected}},indent=2)+'\n',encoding='utf8')
    (work/'PAUSE').write_text('Paused for cost. Further inference requires a new user request and a validated runtime control gate.\n',encoding='utf8')
    print(json.dumps({'state':'draft_prepared_paused','inference_started':False,'work_dir':str(work),'known_blocker':'Capability preflight assertion remains unresolved; no scored end-to-end validation'}))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work-dir',required=True,type=Path,help='New external output directory')
    p.add_argument('--deep',required=True,type=Path,help='Pinned DeepSWE checkout')
    p.add_argument('--pier-source',required=True,type=Path,help='Pinned Pier source checkout')
    p.add_argument('--pier',required=True,type=Path,help='Executable in the pinned Pier environment')
    p.add_argument('--auth-file',required=True,type=Path,help='External existing auth file; its contents are not read during preparation')
    prepare(p.parse_args())
