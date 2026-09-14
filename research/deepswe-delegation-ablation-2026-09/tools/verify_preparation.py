"""Verify preserved instruction edits and paused status without inference."""
import ast
import hashlib
import json
from pathlib import Path

PACKAGE=Path(__file__).resolve().parents[1]
def read(name):return json.loads((PACKAGE/name).read_text(encoding='utf8'))

def verify():
    original=(PACKAGE/'instructions/current.md').read_bytes()
    assert original==(PACKAGE.parent/'deepswe-2026-09/instructions/revised.md').read_bytes()
    revised=original
    for edit in read('instruction-edits.json'):
        old,new=edit['old'].encode('utf8'),edit['new'].encode('utf8')
        assert revised.count(old)==1,edit['reason']
        revised=revised.replace(old,new,1)
    assert revised==(PACKAGE/'instructions/without-subagents.md').read_bytes()
    for term in ['subagent','delegat','Luna/max','descendants']:
        assert term.lower().encode() not in revised.lower()
    status=read('status.json')
    assert status['scored_attempts_started']==0 and status['coding_results'] is None
    assert status['state']=='paused_by_user_for_cost' and not status['automatic_resume']
    assert not status['installed_globals_modified']
    u=status['capability_probes'][0]['usage']
    assert (u['input_tokens']*5+u['output_tokens']*30)/1000000==status['capability_probes'][0]['standard_credit_equivalent']
    for p in PACKAGE.rglob('*.py'):ast.parse(p.read_text(encoding='utf8'),filename=str(p))
    for name in ['instructions/current.md','instructions/without-subagents.md','instruction-edits.json','instructions.patch','runtime.patch','controlled_codex.py']:
        assert hashlib.sha256((PACKAGE/name).read_bytes()).hexdigest()==read('provenance.json')['source_files'][name],name
    print(json.dumps({'status':'verified','instruction_edits':len(read('instruction-edits.json')),'scored_attempts':0,'runtime_gate':'unresolved','inference_started':False}))

if __name__=='__main__':verify()
