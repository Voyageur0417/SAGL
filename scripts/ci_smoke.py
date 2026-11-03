"""Public-only interface checks. No benchmark files, weights, GT or network reads."""
from pathlib import Path
import sys,subprocess,tempfile,json
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from sagl_repro.common import load_config
expected={'sportsmot_ocsort.yaml':('sportsmot',45,2),'sportsmot_diffmot.yaml':('sportsmot',45,2),'soccernet.yaml':('soccernet',20,2),'teamtrack.yaml':('teamtrack',45,1)}
for name,(profile,count,minimum) in expected.items():
 c=load_config(ROOT/'configs'/name)
 assert c['dataset_profile']==profile and len(c['sequences'])==count and c['minimum_observations']==minimum
 assert c['checkpoint_sha256']=='0634e9782792d27ff066e3c20f6c00a93d7bb662c51a4976e39eae2bf36507f9'
for script in ['extract_features.py','run_sagl.py','evaluate.py','verify_predictions.py','verify_reproduction.py']:
 subprocess.run([sys.executable,str(ROOT/'scripts'/script),'--help'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
with tempfile.TemporaryDirectory(prefix='sagl-public-example-') as tmp:
 d=Path(tmp)/'toy';subprocess.run([sys.executable,str(ROOT/'examples/make_synthetic_example.py'),'--output',str(d)],cwd=ROOT,check=True)
 subprocess.run([sys.executable,str(ROOT/'scripts/run_sagl.py'),'--config',str(d/'config.json'),'--cache-dir',str(d/'cache'),'--output',str(d/'prediction')],cwd=ROOT,check=True)
 subprocess.run([sys.executable,str(ROOT/'scripts/verify_predictions.py'),'--carrier',str(d/'carrier/toy.txt'),'--prediction',str(d/'prediction/tracker/data/toy.txt')],cwd=ROOT,check=True)
 q=json.loads((d/'prediction/quantity_stage.json').read_text());assert q[0]['K_current_P']==q[0]['stage2_count']==2
 print('Public smoke PASS: four configurations, five CLI help calls, synthetic linking and ID-only projection. No model/data performance validation implied.')
