"""Portable draft paths; workspace-settings.json is local and never published."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,value):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,indent=2)+'\n',encoding='utf8')

settings=read(ROOT/'workspace-settings.json')
PACKAGE=Path(settings['completed_package'])
PUBLIC=ROOT/'public-export'
DEEP=Path(settings['deep'])
PIER_SOURCE=Path(settings['pier_source'])
PIER=Path(settings['pier'])
AUTH=Path(settings['auth_file'])
OWNER='deepswe-delegation-'+hashlib.sha256(str(ROOT).encode()).hexdigest()[:12]
RATES=read(ROOT/'credit-rates.json')['models']
