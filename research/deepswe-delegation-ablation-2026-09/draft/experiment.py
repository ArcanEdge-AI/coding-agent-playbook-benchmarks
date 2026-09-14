"""DRAFT: capability gate unresolved; no scored end-to-end validation. See README."""
"""Frozen paired execution, native accounting and compact research export."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from prepare import ROOT, PACKAGE, PUBLIC, DEEP, PIER_SOURCE, PIER, AUTH, OWNER, RATES, read, save, sha
from session_accounting import sessions, events

def credits(session):
    assert len(session['models'])==1 and session['usage']
    rates=RATES[session['models'][0]]; u=session['usage']
    assert 0<=u['cached_input_tokens']<=u['input_tokens']
    return sum(v*r/1e6 for v,r in zip([u['input_tokens']-u['cached_input_tokens'],u['cached_input_tokens'],u['output_tokens']],rates))

def verify_preserved(full=False):
    for name,item in read(ROOT/'preservation.json')['files'].items():
        assert sha(ROOT/name)==item, name+' changed'
    if full:
        for label,folder in [('deep-swe',DEEP),('pier',PIER_SOURCE)]:
            for name,digest in read(PACKAGE/'upstream-index.json')[label].items():assert sha(folder/name)==digest,(label,name)
        for task,item in read(PACKAGE/'images.json').items():
            image=json.loads(subprocess.check_output(['docker','image','inspect',item['tag']],text=True,encoding='utf8'))[0]
            assert image['Id']==item['id'] and image['RepoDigests']==item['repo_digests'],task


def config(job,probe=False):
    return {'job_name':job['attempt_id'],'jobs_dir':str(ROOT/'runs'),'n_attempts':1,'n_concurrent_trials':1,'quiet':True,
      'retry':{'max_retries':0},'environment':{'import_path':'controlled_codex:CalibrationDocker','delete':False},
      'agents':[{'import_path':'controlled_codex:CleanCodex','model_name':'openai/'+job['model'],'override_timeout_sec':1200,
      'kwargs':{'version':'0.154.0-alpha.6.2','reasoning_effort':'high','arm':job['arm']},
      'env':{'CODEX_AUTH_JSON_PATH':str(AUTH)}}], 'tasks':[{'path':str(DEEP/'tasks'/job['task'])}]}

def freeze():
    assert not (ROOT/'manifest.json').exists(),'Already frozen'
    assert read(ROOT/'probe-status.json')['state']=='passed'
    verify_preserved(full=True)
    tasks=list(read(PACKAGE/'acceptance-tests.json'))
    blocks=[]
    for model in RATES:
        for task in tasks:
            for repeat in (1,2):
                key=f'{model}/{task}/{repeat}'
                blocks.append({'model':model,'task':task,'repeat':repeat,'sort':hashlib.sha256(('delegation-ablation-20260913/'+key).encode()).hexdigest()})
    blocks.sort(key=lambda b:b['sort']); pairs=[]
    for index,b in enumerate(blocks,1):
        flip=int(hashlib.sha256((b['model']+'/'+b['task']).encode()).hexdigest(),16)%2
        arms=['current','without-subagents']
        if (flip+b['repeat'])%2:arms.reverse()
        pair={'pair_id':f'pair-{index:02}','model':b['model'],'task':b['task'],'repeat':b['repeat'],'jobs':[]}
        for arm in arms:
            job={'attempt_id':f'ab-{index:02}-'+('on' if arm=='current' else 'off'),'pair_id':pair['pair_id'],
                 'model':b['model'],'effort':'high','task':b['task'],'repeat':b['repeat'],'arm':arm}
            pair['jobs'].append(job);save(ROOT/'configs'/(job['attempt_id']+'.json'),config(job))
        pairs.append(pair)
    fixed=['PLAN.md','instructions/current.md','instructions/without-subagents.md','instruction-edits.json','instructions.patch',
           'controlled_codex.py','runtime.patch','prepare.py','experiment.py','session_accounting.py','credit-rates.json','preservation.json']
    fixed+=['configs/'+j['attempt_id']+'.json' for p in pairs for j in p['jobs']]
    save(ROOT/'manifest.json',{'state':'prepared','created_at':datetime.now(timezone.utc).isoformat(),
         'design':'Current globals versus only delegation instructions removed and native agents disabled; repeated paired package ablation',
         'pairs':pairs,'root_start_cap':48,'capability_probe_roots':2,'concurrency':2,'credit_guard':4000,
         'files':{n:sha(ROOT/n) for n in fixed},'global_sha256':sha(ROOT/'instructions/current.md'),
         'without_subagents_sha256':sha(ROOT/'instructions/without-subagents.md')})
    export('prepared',[])
    print('Frozen 24 pairs / 48 scored starts.',flush=True)

def normalized_startup(folder,arm):
    data=read(folder/'agent/startup-input.json')
    global_text=(ROOT/'instructions'/(arm+'.md')).read_text(encoding='utf8').strip()
    result=[]
    for item in data:
        s='\n'.join(c.get('text','') for c in item.get('content',[])).replace('\r\n','\n')
        if s.startswith(('<multi_agent_role>','<multi_agent_mode>')):continue
        s=s.replace(global_text,'FROZEN_GLOBAL_TREATMENT')
        s=re.sub(r'<current_date>[^<]+</current_date>','<current_date>RUNTIME_DATE</current_date>',s)
        s=re.sub(r'/opt/calibration/codex-home/tmp/arg0/codex-arg0[A-Za-z0-9]+','/opt/calibration/codex-home/tmp/arg0/codex-arg0RUNTIME_SUFFIX',s)
        result.append((item.get('role'),s))
    return result

def audit(job,trial):
    folder=trial.parent;result=read(trial)
    exception=(result.get('exception_info') or {}).get('exception_type')
    assert exception in (None,'AgentTimeoutError'),(job['attempt_id'],exception)
    pre=read(folder/'agent/preflight.json')
    assert pre['arm']==job['arm'] and pre['model']=='openai/'+job['model'] and not pre['smoke'] and not pre['probe_only']
    assert pre['global_sha256']==sha(ROOT/'instructions'/(job['arm']+'.md')) and pre['global_present_exactly_once']
    assert pre['agents_enabled']==(job['arm']=='current')
    reward=read(folder/'verifier/reward.json');tests=read(folder/'verifier/ctrf.json')['results']['tests']
    names=Counter(t['name'] for t in tests)
    assert names==Counter(read(PACKAGE/'acceptance-tests.json')[job['task']])
    for group in ('f2p','p2p'):
        checks=[t for t in tests if t['name'].startswith('['+group+'] ')]
        assert len(checks)==reward[group+'_total'] and sum(t['status']=='passed' for t in checks)==reward[group+'_passed']
    assert reward['reward']==int(reward['f2p_total']>0 and reward['f2p_passed']==reward['f2p_total'] and reward['p2p_passed']==reward['p2p_total'])
    acc=sessions(folder)
    assert acc['root']['models']==[job['model']] and acc['root']['efforts']==['high']
    assert not acc['usage_missing_session_ids'] and not acc['accounting_anomaly_count'] and acc['helper_routes_compliant']
    if job['arm']=='without-subagents':assert acc['helper_count']==0,'DISABLED ARM SPAWNED HELPER'
    stream=events(Path(acc['root']['path']));meta=next(e['payload'] for e in stream if e.get('type')=='session_meta')
    assert meta['cli_version']=='0.154.0-alpha.6.2'
    base_sha=hashlib.sha256(json.dumps(meta['base_instructions'],sort_keys=True).encode()).hexdigest()
    patch=folder/'artifacts/model.patch'
    row={**job,'status':'timeout' if exception else 'completed','reward':reward,'helpers':acc['helper_count'],
        'credits':sum(credits(s) for s in acc['sessions']),'helper_credits':sum(credits(s) for s in acc['helpers']),
        'native_seconds':read(folder/'agent/inference-timing.json')['seconds'],
        'patch_bytes':patch.stat().st_size,'patch_sha256':sha(patch),'ctrf_sha256':sha(folder/'verifier/ctrf.json'),
        'native_base_sha256':base_sha,'session_usage':[{'role':'helper' if s['parent_id'] else 'root','models':s['models'],'efforts':s['efforts'],'usage':s['usage']} for s in acc['sessions']],
        'test_statuses':[{k:t[k] for k in ('name','status')} for t in tests]}
    save(ROOT/'accounting'/(job['attempt_id']+'.json'),acc)
    return row

def run_one(job):
    name=job['attempt_id'];marker=ROOT/'starts'/(name+'.json')
    marker.parent.mkdir(exist_ok=True)
    with marker.open('x',encoding='utf8') as stream:json.dump({**job,'started_at':datetime.now(timezone.utc).isoformat()},stream)
    assert not (ROOT/'runs'/name).exists()
    print('Starting '+name+' '+job['model']+' '+job['task'],flush=True)
    env={**os.environ,'PYTHONPATH':str(ROOT),'PYTHONUTF8':'1','PYTHONDONTWRITEBYTECODE':'1','NO_COLOR':'1'}
    for key in ['OPENAI_API_KEY','OPENAI_BASE_URL','OPENAI_API_BASE','CODEX_FORCE_AUTH_JSON']:env.pop(key,None)
    with (ROOT/'configs'/(name+'.log')).open('w',encoding='utf8') as log:
        proc=subprocess.run([str(PIER),'run','-c',str(ROOT/'configs'/(name+'.json'))],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    results=[p for p in (ROOT/'runs'/name).rglob('result.json') if p.parent!=ROOT/'runs'/name]
    assert len(results)==1,(name,'missing result',proc.returncode)
    save(ROOT/'trial-paths'/(name+'.json'),{'path':str(results[0])})
    row=audit(job,results[0]);save(ROOT/'outcomes'/(name+'.json'),row)
    print(json.dumps({k:row[k] for k in ['attempt_id','status','reward','helpers','credits']}),flush=True)
    return row,results[0].parent

def cleanup():
    def docker(*args):return subprocess.check_output(['docker',*args],text=True,encoding='utf8').strip()
    ids=docker('ps','-aq','--filter','label=codex.benchmark.owner='+OWNER).split()
    removed=[]
    for cid in ids:
        info=json.loads(docker('inspect',cid))[0];labels=info['Config'].get('Labels') or {}
        assert labels.get('codex.benchmark.owner')==OWNER
        project=labels.get('com.docker.compose.project');assert project
        peers=docker('ps','-aq','--filter','label=com.docker.compose.project='+project).split()
        for peer in peers:
            record=json.loads(docker('inspect',peer))[0]
            assert (record['Config'].get('Labels') or {}).get('com.docker.compose.project')==project
            if record['State']['Running']:docker('stop','--time','10',peer)
            docker('rm',peer);removed.append(record['Name'].lstrip('/'))
        for network in docker('network','ls','-q','--filter','label=com.docker.compose.project='+project).split():
            record=json.loads(docker('network','inspect',network))[0]
            assert record['Labels'].get('com.docker.compose.project')==project and not record.get('Containers')
            docker('network','rm',network)
    return removed

def export(state,rows):
    PUBLIC.mkdir(parents=True,exist_ok=True)
    for name in ['instructions/current.md','instructions/without-subagents.md','instruction-edits.json','instructions.patch','credit-rates.json','runtime.patch','controlled_codex.py']:
        target=PUBLIC/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
    shutil.copyfile(ROOT/'PLAN.md',PUBLIC/'protocol.md')
    save(PUBLIC/'schedule.json',read(ROOT/'manifest.json')['pairs'])
    save(PUBLIC/'outcomes.json',{'state':state,'records':rows})
    aggregates={}
    for arm in ['current','without-subagents']:
        selected=[r for r in rows if r['arm']==arm];passed=sum(r['reward']['reward'] for r in selected)
        total=sum(r['credits'] for r in selected)
        aggregates[arm]={'attempts':len(selected),'full_passes':passed,'credits':total,'helper_credits':sum(r['helper_credits'] for r in selected),
            'helpers':sum(r['helpers'] for r in selected),'credits_per_full_pass':total/passed if passed else None,
            'timeouts':sum(r['status']=='timeout' for r in selected),'empty_patches':sum(r['patch_bytes']==0 for r in selected)}
    pairs=[]
    for p in read(ROOT/'manifest.json')['pairs']:
        matches={r['arm']:r for r in rows if r['pair_id']==p['pair_id']}
        if len(matches)==2:
            on,off=matches['current'],matches['without-subagents']
            pairs.append({'pair_id':p['pair_id'],'model':p['model'],'task':p['task'],'repeat':p['repeat'],
                          'current_pass':on['reward']['reward'],'without_subagents_pass':off['reward']['reward'],
                          'current_minus_without_credits':on['credits']-off['credits']})
    report={'state':state,'completed_scored_attempts':len(rows),'planned_scored_attempts':48,'arms':aggregates,'paired_outcomes':pairs,
            'limitations':['Known tasks, two repetitions, three task clusters; no universal causal claim.',
            'Treatment changes delegation instructions and native capability together.',
            'Upstream oracle ambiguities and undisclosed 20-minute author deadline retained.',
            'Recorded Standard credit equivalent, not actual billing ledger; interrupted final requests may be missing.',
            'Raw full-pass outcome, subject to manual investigation of any grader-overlay interference.']}
    save(ROOT/'results.json',report);save(PUBLIC/'results.json',report)
    lines=['# Current-global delegation ablation','',f'Status: **{state}**. Scored attempts: **{len(rows)}/48**.','',
       'Current installed globals are compared with a copy containing only delegation-related removals and native subagent tools disabled. Installed globals were not modified. See [protocol](protocol.md), [instruction diff](instructions.patch), [session usage and test outcomes](outcomes.json).','',
       '| Condition | Attempts | Full passes | Standard credits | Helper credits | Credits/full pass |','|---|---:|---:|---:|---:|---:|']
    for arm,a in aggregates.items():
        ratio=f"{a['credits_per_full_pass']:.2f}" if a['credits_per_full_pass'] is not None else 'undefined'
        lines.append(f"| {arm} | {a['attempts']} | {a['full_passes']} | {a['credits']:.2f} | {a['helper_credits']:.2f} | {ratio} |")
    lines+=['','All failed and timed-out attempts with valid accounting are included in cost. Probe usage is separate. These are credit equivalents using [published Standard rates](https://learn.chatgpt.com/docs/pricing#token-rates), not measured Pro allowance or purchased-credit deductions.','',
            'Two repeats on each of three known tasks are exploratory. Preserve the original grades; known oracle ambiguity limits correctness claims. A result with no helpers in the enabled arm measures the availability/instruction package, not the effect of actual helper execution.','',
            'Full native transcripts, patches and raw verifier evidence remain in the local archive. This compact package contains no credentials or raw transcripts.']
    (PUBLIC/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    (ROOT/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf8')

def run():
    manifest=read(ROOT/'manifest.json');assert manifest['state']=='prepared','No implicit resume or retry'
    verify_preserved(full=True)
    for name,digest in manifest['files'].items():assert sha(ROOT/name)==digest,name
    manifest['state']='running';save(ROOT/'manifest.json',manifest)
    rows=[];cleanup_records=[];state='running';error=None
    try:
        cleanup_records+=cleanup()
        for pair in manifest['pairs']:
            if (ROOT/'PAUSE').exists():state='paused';break
            if sum(r['credits'] for r in rows)>=manifest['credit_guard']:state='credit_guard_reached';break
            verify_preserved()
            for name,digest in manifest['files'].items():assert sha(ROOT/name)==digest,name
            with ThreadPoolExecutor(max_workers=2) as pool:
                futures=[pool.submit(run_one,j) for j in pair['jobs']]
                completed=[f.result() for f in futures]
            (a,ap),(b,bp)=completed
            assert normalized_startup(ap,a['arm'])==normalized_startup(bp,b['arm']),'Unexpected paired startup difference'
            assert a['native_base_sha256']==b['native_base_sha256'],'Paired native base drift'
            ac=read(ap/'agent/preflight.json');bc=read(bp/'agent/preflight.json')
            assert ac['instruction_sha256']==bc['instruction_sha256'],'Task prompt drift'
            assert [f for f in ac['config_flags'] if not f.startswith('agents.enabled=')]==[f for f in bc['config_flags'] if not f.startswith('agents.enabled=')]
            save(ROOT/'pair-audits'/(pair['pair_id']+'.json'),{'passed':True,'startup_equal_except_treatment':True,'task_prompt_equal':True,'other_flags_equal':True})
            rows.extend([a,b]);cleanup_records+=cleanup();export('running',rows)
        else:state='completed'
    except Exception as exc:
        state='needs_attention';error=repr(exc)
        # Retain completed evidence even if a sibling or paired gate failed.
        rows=[read(p) for p in sorted((ROOT/'outcomes').glob('*.json'))] if (ROOT/'outcomes').exists() else []
        print('STOP: '+error,flush=True)
    finally:
        try:cleanup_records+=cleanup()
        except Exception as exc:state='needs_attention';error=(error or '')+' Cleanup: '+repr(exc)
        verify_preserved(full=True)
        manifest.update(state=state,finished_at=datetime.now(timezone.utc).isoformat(),completed_attempts=len(rows),error=error)
        save(ROOT/'manifest.json',manifest);save(ROOT/'disposition.json',{'removed_owned_containers':cleanup_records,'auxiliary_worktrees':0,'installed_globals_unchanged':True})
        export(state,rows)
        print(json.dumps({'state':state,'completed':len(rows),'credits':sum(r['credits'] for r in rows),'error':error}),flush=True)
    if state=='completed':
        index={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and not any(x in p.parts for x in ['probe-home','runtime-schema','__pycache__']) and p.name not in ['driver.log','driver.err','evidence-index.json']}
        save(ROOT/'evidence-index.json',index)
        save(PUBLIC/'provenance.json',{'state':state,'local_archive':'deepswe-delegation-ablation-v1','evidence_index_sha256':sha(ROOT/'evidence-index.json'),
             'files':len(index),'current_global_sha256':manifest['global_sha256'],'without_subagents_sha256':manifest['without_subagents_sha256'],
             'native_cli':'0.154.0-alpha.6.2','deep_swe_commit':'0b9fabbb63b9104d678fe965e1632f2dd9eaa2ea','pier_commit':'0c802fc067a425345b24d1c69411aa98acf61a1d'})

if __name__=='__main__':
    {'freeze':freeze,'run':run}[sys.argv[1]]()
