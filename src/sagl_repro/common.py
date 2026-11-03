import json, hashlib
from pathlib import Path

def sha256(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def dump(path,value):
 Path(path).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')

def load_config(path):
 path=Path(path).resolve()
 if path.suffix.lower()=='.json': c=json.loads(path.read_text())
 else:
  import yaml
  c=yaml.safe_load(path.read_text())
 if c['dataset_profile'] not in ('sportsmot','soccernet','teamtrack'):raise ValueError('unknown dataset_profile')
 if len({s['name'] for s in c['sequences']})!=len(c['sequences']):raise ValueError('duplicate sequence')
 def resolve(v):return str((path.parent/Path(v)).resolve())
 c['carrier_root']=resolve(c['carrier_root'])
 for key in ('checkpoint','embedding_cache','embedding_keys'):
  if key in c:c[key]=resolve(c[key])
 for s in c['sequences']:
  if '/' in s['name'] or s['name'] in ('.','..'):raise ValueError('sequence must be a basename')
  if float(s['fps'])<=0:raise ValueError('FPS must be positive')
  for key in ('images','video'):
   if key in s and s[key] is not None:s[key]=resolve(s[key])
 minimum=1 if c['dataset_profile']=='teamtrack' else 2
 if c.get('minimum_observations',minimum)!=minimum:raise ValueError('minimum observations differs from frozen profile')
 c['minimum_observations']=minimum
 return c
