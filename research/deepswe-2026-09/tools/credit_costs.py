"""Recompute Standard Codex credit equivalents from audited session usage.

Run with --check to verify the checked-in JSON without writing anything.
No model calls, credentials, network access or billing operations are used.
"""
from collections import defaultdict
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parents[1]

def read(name):
    return json.loads((PACKAGE/name).read_text(encoding='utf8'))

def compute():
    rates=read('credit-rates.json')['models']
    records=read('graded-outcomes.json')['outcomes']
    arms={}
    common={}
    for arm in ['none','previous','revised']:
        rows=[r for r in records if r['arm']==arm]
        def summarize(selected):
            buckets=defaultdict(Decimal)
            models=defaultdict(Decimal)
            for row in selected:
                for session in row['session_usage']:
                    assert len(session['models'])==1 and session['usage'] is not None
                    model=session['models'][0];u=session['usage']
                    assert u['input_tokens']>=u['cached_input_tokens']>=0
                    values=[u['input_tokens']-u['cached_input_tokens'],u['cached_input_tokens'],u['output_tokens']]
                    parts=[Decimal(n)*Decimal(str(r))/Decimal(1000000) for n,r in zip(values,rates[model])]
                    cost=sum(parts)
                    buckets['total']+=cost;buckets[session['role']]+=cost;models[model]+=cost
                    for key,value in zip(['uncached_input','cached_input','output'],parts):buckets[key]+=value
            passed=sum(r['reward']['reward'] for r in selected)
            return {'attempts':len(selected),'raw_full_passes':passed,'helpers':sum(r['helpers'] for r in selected),
                'credits':{k:float(buckets[k]) for k in ['total','root','helper','uncached_input','cached_input','output']},
                'credits_by_model':{k:float(v) for k,v in sorted(models.items())},
                'helper_credit_share_percent':float(100*buckets['helper']/buckets['total']) if buckets['total'] else None,
                'credits_per_raw_full_pass':float(buckets['total']/passed) if passed else None}
        arms[arm]=summarize(rows)
        common[arm]=summarize([r for r in rows if not r['attempt'].endswith('010')])
    return {'status':'recomputed_from_recorded_usage','pricing':'Standard credit equivalent; not a billing ledger',
        'source_usage_sha256':hashlib.sha256((PACKAGE/'graded-outcomes.json').read_bytes()).hexdigest(),
        'rate_card_sha256':hashlib.sha256((PACKAGE/'credit-rates.json').read_bytes()).hexdigest(),
        'all_18_attempts_per_arm':arms,'matched_17_excluding_baseline_grader_interference':common,
        'total_scored_credit_equivalent':float(sum(Decimal(str(v['credits']['total'])) for v in arms.values()))}

if __name__=='__main__':
    result=compute()
    if '--check' in sys.argv:
        assert result==read('credits.json'),'Recorded credit analysis does not match usage and rate card'
        print(json.dumps({'status':'verified','scored_attempts':54,'credits':result['total_scored_credit_equivalent']}))
    else:
        (PACKAGE/'credits.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
        print('Wrote credits.json from the existing 54 scored outcomes; no inference.')
