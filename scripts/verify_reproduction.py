"""Compare two independent SAGL runs and observation caches; no inference/GT fitting."""
from pathlib import Path
import sys,json,argparse
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
import numpy as np
from sagl_repro.common import dump,sha256
from sagl_repro.features import read_rows
ap=argparse.ArgumentParser()
ap.add_argument('--reference-inference',required=True);ap.add_argument('--candidate-inference',required=True);ap.add_argument('--reference-cache');ap.add_argument('--candidate-cache');ap.add_argument('--carrier-root',required=True);ap.add_argument('--report',required=True)
a=ap.parse_args();ref=Path(a.reference_inference);new=Path(a.candidate_inference);report={}
def arrays(file):
 x=np.load(ref/file);y=np.load(new/file)
 pairkeys=['sequence_index','source','destination']
 pairs=lambda z:set(zip(*(z[k].tolist() for k in pairkeys)))
 d={'array_equal':set(x.files)==set(y.files) and all(x[k].shape==y[k].shape and np.array_equal(x[k],y[k],equal_nan=True) for k in x.files),'count_reference':len(x[x.files[0]]),'count_candidate':len(y[y.files[0]])}
 if all(k in x.files for k in pairkeys):
  xx=pairs(x);yy=pairs(y);d.update(pairs_added=len(yy-xx),pairs_removed=len(xx-yy))
 if 'score' in x.files and 'score' in y.files and x['score'].shape==y['score'].shape:d['max_score_abs_difference']=float(np.max(np.abs(x['score']-y['score']))) if len(x['score']) else 0.
 return d
for file in ['all_feasible_scores.npz','candidate_graph.npz','qualified_graph.npz']:
 if (ref/file).exists() and (new/file).exists():report[file]=arrays(file)
x=np.load(ref/'edge_sets.npz');y=np.load(new/'edge_sets.npz')
report['matching']={k:{'count_reference':len(x[k]),'count_candidate':len(y[k]),'set_equal':set(map(int,x[k]))==set(map(int,y[k])),'order_equal':np.array_equal(x[k],y[k])} for k in ['current_P','accepted']}
report['K_equal']=report['matching']['current_P']['count_reference']==report['matching']['current_P']['count_candidate'];report['ID_map_equal']=json.loads((ref/'id_map.json').read_text())==json.loads((new/'id_map.json').read_text())
report['predictions']=[]
for p in sorted((new/'tracker/data').glob('*.txt')):
 q=ref/'tracker/data'/p.name;carrier=Path(a.carrier_root)/p.name;ca=read_rows(carrier);cb=read_rows(p);cr=read_rows(q)
 nonid=len(ca)==len(cb) and all(v[:1]+v[2:]==w[:1]+w[2:] for (_,v),(_,w) in zip(ca,cb))
 report['predictions'].append({'sequence':p.stem,'reference_SHA256':sha256(q),'candidate_SHA256':sha256(p),'byte_equal':p.read_bytes()==q.read_bytes(),'non_ID_and_order_preserved':nonid,'rows':len(cb),'different_prediction_rows':sum(v!=w for (_,v),(_,w) in zip(cr,cb))+abs(len(cr)-len(cb))})
cache_exact=True
if a.reference_cache and a.candidate_cache:
 rc=Path(a.reference_cache);nc=Path(a.candidate_cache);x=np.load(rc/'features.npy').astype(np.float64);y=np.load(nc/'features.npy').astype(np.float64);keys=lambda p:json.loads((p/'features.keys.json').read_text());samekeys=keys(rc)==keys(nc)
 if x.shape!=y.shape:raise ValueError('cache shape mismatch')
 nx=np.linalg.norm(x,axis=1);ny=np.linalg.norm(y,axis=1);v=(nx>0)&(ny>0);cos=(x[v]*y[v]).sum(1)/(nx[v]*ny[v]);diff=np.abs(x-y);cache_exact=bool(np.array_equal(x,y))
 report['cache']={'count':len(y),'shape':list(y.shape),'dtype_reference':str(np.load(rc/'features.npy',mmap_mode='r').dtype),'dtype_candidate':str(np.load(nc/'features.npy',mmap_mode='r').dtype),'key_mapping_equal':samekeys,'finite':bool(np.isfinite(y).all()),'zero_reference':int((nx==0).sum()),'zero_candidate':int((ny==0).sum()),'norm_min':float(ny.min()),'norm_max':float(ny.max()),'cosine_min':float(cos.min()) if len(cos) else None,'cosine_mean':float(cos.mean()) if len(cos) else None,'max_abs_difference':float(diff.max()) if diff.size else 0.,'mean_abs_difference':float(diff.mean()) if diff.size else 0.,'bitwise_equal':cache_exact,'unequal_rows':int(np.any(x!=y,axis=1).sum())}
 mapping_ok=samekeys and report['cache']['finite']
else:mapping_ok=True
prediction_equal=all(p['byte_equal'] and p['non_ID_and_order_preserved'] for p in report['predictions'])
output_equal=prediction_equal and report['ID_map_equal'] and report['K_equal'] and report['matching']['accepted']['set_equal'] and mapping_ok
intermediate_equal=all(v['array_equal'] for k,v in report.items() if k.endswith('.npz')) and all(v['order_equal'] for v in report['matching'].values())
report['status']='EXACT_MATCH' if output_equal and intermediate_equal and cache_exact else 'NUMERICALLY_EQUIVALENT' if output_equal else 'NOT_REPRODUCED'
report['scope']='Only the supplied sequences are validated. Numerical equivalence denotes identical final links/maps/predictions; intermediate scores or graph membership can differ.'
dump(a.report,report);print(json.dumps(report,indent=2))
if not output_equal:raise SystemExit(2)
