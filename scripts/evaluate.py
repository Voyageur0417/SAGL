"""Evaluate predictions only; never imported by feature extraction or inference."""
from pathlib import Path
import sys,json,argparse,shutil,hashlib,time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'vendor')]
import numpy as np
from sagl_repro.common import load_config,dump,sha256
# Original TrackEval snapshot uses these aliases. Its source/metrics are unchanged.
if 'float' not in np.__dict__: np.float=float
if 'int' not in np.__dict__: np.int=int
import trackeval
ap=argparse.ArgumentParser(description='Separate standard TrackEval evaluation; requires legally obtained GT')
ap.add_argument('--config',required=True);ap.add_argument('--gt-root',required=True);ap.add_argument('--predictions',required=True,help='directory containing SEQUENCE.txt files');ap.add_argument('--output',required=True)
a=ap.parse_args();c=load_config(a.config);out=Path(a.output);out.mkdir(parents=True,exist_ok=False);pred=Path(a.predictions).resolve();gt=Path(a.gt_root).resolve()
for s in c['sequences']:
 name=s['name'];q=out/'tracker/data'/(name+'.txt');q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(pred/(name+'.txt'),q)
(out/'seqmap.txt').write_text('name\n'+'\n'.join(s['name'] for s in c['sequences'])+'\n')
sports=c['dataset_profile']=='sportsmot'
dc={'GT_FOLDER':str(gt),'TRACKERS_FOLDER':str(out.resolve()),'TRACKERS_TO_EVAL':['tracker'],'BENCHMARK':'SportsMOT' if sports else 'MOT17','SPLIT_TO_EVAL':'val' if sports else 'train','SKIP_SPLIT_FOL':True,'DO_PREPROC':sports,'SEQMAP_FILE':str((out/'seqmap.txt').resolve()),'TRACKER_SUB_FOLDER':'data','PRINT_CONFIG':False}
ds=trackeval.datasets.MotChallenge2DBox(dc)
ev=trackeval.Evaluator({'USE_PARALLEL':False,'PRINT_CONFIG':False,'PRINT_RESULTS':False,'PLOT_CURVES':False,'TIME_PROGRESS':False,'DISPLAY_LESS_PROGRESS':True,'BREAK_ON_ERROR':True,'LOG_ON_ERROR':str((out/'errors.log').resolve())})
def clean(v):
 if isinstance(v,np.ndarray):return v.tolist()
 if isinstance(v,np.generic):return v.item()
 if isinstance(v,dict):return {str(k):clean(x) for k,x in v.items()}
 if isinstance(v,(tuple,list)):return [clean(x) for x in v]
 return v
t=time.perf_counter();raw,status=ev.evaluate([ds],[trackeval.metrics.HOTA(),trackeval.metrics.CLEAR(),trackeval.metrics.Identity()])
if status[ds.get_name()]['tracker']!='Success':raise RuntimeError(status)
r=raw[ds.get_name()]['tracker'];dump(out/'trackeval_raw.json',clean(r))
def metrics(m):
 return {**{k:float(np.mean(m['HOTA'][k])*100) for k in ['HOTA','DetA','AssA']},'IDF1':float(m['Identity']['IDF1']*100),'MOTA':float(m['CLEAR']['MOTA']*100),'IDSW':int(m['CLEAR']['IDSW']),'FP':int(m['CLEAR']['CLR_FP']),'FN':int(m['CLEAR']['CLR_FN'])}
result={'scope':'LOCAL_VALIDATION_REPRODUCTION_NOT_OFFICIAL_TEST','combined':metrics(r['COMBINED_SEQ']['pedestrian']),'per_sequence':{s:metrics(m['pedestrian']) for s,m in r.items() if s!='COMBINED_SEQ'}}
dump(out/'metrics.json',result);dump(out/'evaluation_manifest.json',{'GT_read':True,'used_for_inference':False,'config':ds.config,'evaluator':ev.config,'trackeval_source':json.loads((ROOT/'manifests/trackeval_source_manifest.json').read_text()),'GT_sha256':{s['name']:sha256(gt/s['name']/'gt/gt.txt') for s in c['sequences']},'prediction_sha256':{s['name']:sha256(pred/(s['name']+'.txt')) for s in c['sequences']},'elapsed_seconds':time.perf_counter()-t});print(json.dumps(result,indent=2))
