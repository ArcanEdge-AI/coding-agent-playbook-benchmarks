"""Run and retain two bounded native capability controls before scoring."""
import os
import subprocess
from prepare import ROOT, DEEP, PIER, AUTH, save, read
from session_accounting import sessions

def config(arm):
    name='probe-'+arm
    return {'job_name':name,'jobs_dir':str(ROOT/'probes'),'n_attempts':1,'n_concurrent_trials':1,'quiet':True,
        'retry':{'max_retries':0},'environment':{'import_path':'controlled_codex:CalibrationDocker','delete':False},
        'verifier':{'disable':True},'agents':[{'import_path':'controlled_codex:CleanCodex','model_name':'openai/gpt-5.6-luna',
        'override_timeout_sec':240,'kwargs':{'version':'0.154.0-alpha.6.2','reasoning_effort':'max','arm':arm,'smoke':True},
        'env':{'CODEX_AUTH_JSON_PATH':str(AUTH)}}],
        'tasks':[{'path':str(DEEP/'tasks/python-statemachine-state-data-scoping')}]}

if __name__=='__main__':
    if (ROOT/'PAUSE').exists():
        raise SystemExit('Paused. Do not start inference without a new user request and explicit budget.')
    env={**os.environ,'PYTHONPATH':str(ROOT),'PYTHONUTF8':'1','PYTHONDONTWRITEBYTECODE':'1','NO_COLOR':'1'}
    for key in ['OPENAI_API_KEY','OPENAI_BASE_URL','OPENAI_API_BASE','CODEX_FORCE_AUTH_JSON']:env.pop(key,None)
    records=[]
    for arm in ['without-subagents','current']:
        cfg=config(arm);name=cfg['job_name'];path=ROOT/'probe-configs'/(name+'.json')
        assert not (ROOT/'probes'/name).exists(),'Do not repeat probe starts'
        save(path,cfg)
        print('Starting '+name,flush=True)
        with path.with_suffix('.log').open('w',encoding='utf8') as log:
            r=subprocess.run([str(PIER),'run','-c',str(path)],env=env,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        results=[p for p in (ROOT/'probes'/name).rglob('result.json') if p.parent!=ROOT/'probes'/name]
        assert len(results)==1,(name,'missing result')
        result=read(results[0]);save(ROOT/'probe-status.json',{'state':'checking','latest':name,'result':str(results[0])})
        assert not result.get('exception_info'),(name,result.get('exception_info'))
        acc=sessions(results[0].parent)
        assert acc['helper_count']==int(arm=='current'),(name,acc['helper_count'])
        assert acc['helper_routes_compliant'] and not acc['usage_missing_session_ids'] and not acc['accounting_anomaly_count']
        assert acc['root']['models']==['gpt-5.6-luna'] and acc['root']['efforts']==['max']
        records.append({'arm':arm,'passed':True,'accounting':acc,'trial':str(results[0].parent)})
        save(ROOT/'probe-status.json',{'state':'passed' if len(records)==2 else 'running','records':records})
        print(name+' passed: helpers='+str(acc['helper_count']),flush=True)
