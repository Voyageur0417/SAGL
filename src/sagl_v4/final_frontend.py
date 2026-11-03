"""GT-free V3 front-end. Original observation cache only; no model or GT fitting."""
import json,time,math
from pathlib import Path
from collections import defaultdict
import numpy as np
from .final_prototypes import prototype_bundle,proto_similarity,l2n

def read_tracks(carrier_root,sequences,min_observations):
 tracks={};rowcounts={}
 for seq in sequences:
  lines=[ln.split(',') for ln in (Path(carrier_root)/(seq+'.txt')).read_text().splitlines() if ln.strip()];rowcounts[seq]=len(lines);by=defaultdict(list)
  for r in lines:
   assert len(r)>=7 and float(r[0]).is_integer() and float(r[1]).is_integer();by[int(float(r[1]))].append(r)
  tt=[]
  for tid,rr in sorted(by.items()):
   rr.sort(key=lambda r:int(float(r[0])));frames=[int(float(r[0])) for r in rr];assert len(set(frames))==len(frames),('duplicate frame within original ID',seq,tid)
   if len(rr)<min_observations:continue
   tt.append({'sequence':seq,'tid':tid,'rows':rr,'start':min(frames),'end':max(frames),'length':len(rr)})
  tracks[seq]=tt
 return tracks,rowcounts

def attach_cached_features(tracks,cache,keys_path,variant='R4'):
 feat=np.load(cache,mmap_mode='r');keys=json.loads(Path(keys_path).read_text());keys=keys.get('keys',keys) if isinstance(keys,dict) else keys;assert feat.shape==(len(keys),512);by=defaultdict(list)
 for i,k in enumerate(keys):by[k['sequence'],int(k.get('tid',k.get('track_id')))].append(i)
 stats=[]
 for seq,trs in tracks.items():
  for tr in trs:
   ix=by[seq,tr['tid']];assert len(ix)==len(tr['rows'])
   for j,ind in enumerate(ix):
    k=keys[ind];row=tr['rows'][j];assert int(k['frame'])==int(float(row[0]));assert abs(float(k['score'])-float(row[6]))<1e-6
    if 'bbox' in k:np.testing.assert_array_equal(k['bbox'],list(map(float,row[2:6])))
    if 'area' in k:assert abs(float(k['area'])-float(row[4])*float(row[5]))<1e-5
   f=np.asarray(feat[ix],np.float32);assert np.isfinite(f).all();metas=[keys[i] for i in ix];p=prototype_bundle(f,metas);mean=p['mean'];disp=p['dispersion'];anchors=sorted({0,len(f)//2,len(f)-1});quality=[i for _,i in sorted([(math.log1p(float(k.get('area',0)))+.2*float(k.get('score',1)),j) for j,k in enumerate(metas)],reverse=True)[:min(5,len(f))]]
   def dedup(raw):
    vv=[];seen=set()
    for v in raw:
     key=tuple(np.round(v[:8],4))
     if key not in seen:seen.add(key);vv.append(l2n(v))
    return np.asarray(vv,np.float32)
   if variant=='R0':p={**p,'robust':mean[None,:],'dispersion':0.}
   elif variant=='R1':p={**p,'robust':mean[None,:]}
   elif variant=='R2':p={**p,'robust':dedup([mean,*f[anchors]])}
   elif variant=='R3':p={**p,'robust':dedup([mean,*f[quality]])}
   elif variant=='R5':p={**p,'dispersion':0.}
   elif variant!='R4':raise ValueError(variant)
   tr['proto']=p;stats.append({'sequence':seq,'track_id':tr['tid'],'observations':len(f),'prototype_count':len(p['robust']),'dispersion':disp,'anchor_indices':anchors,'quality_indices':quality,'quality_area_available':all('area' in k for k in metas)})
 return stats

def score_all(tracks,sequences,fps_by_sequence):
 columns={k:[] for k in ['sequence_index','source','destination','tier','gap_seconds','score','sim_max','sim_topk_mean','sim_mean']}
 for sq,seq in enumerate(sequences):
  fps=float(fps_by_sequence[seq]);assert fps>0
  for src in tracks[seq]:
   for dst in tracks[seq]:
    gap=dst['start']-src['end']-1
    if src['tid']==dst['tid'] or gap<0:continue
    sec=gap/fps;sim=proto_similarity(src,dst,'robust');values={'sequence_index':sq,'source':src['tid'],'destination':dst['tid'],'tier':int(np.searchsorted([1.,3.,10.,30.],sec,side='right')),'gap_seconds':sec,**sim}
    for key in columns:columns[key].append(values[key])
 out={k:np.asarray(v,np.int64 if k in ['sequence_index','source','destination','tier'] else np.float64) for k,v in columns.items()};out['edge_id']=np.arange(len(out['score']),dtype=np.int64);return out

def sparse_qualify(base,sequences,budget=10,gate='dual',shared_floor=False,unstratified=False,max_gap=None):
 n=len(base['score']);groups=defaultdict(list)
 for i in range(n):groups[(int(base['sequence_index'][i]),int(base['source'][i]),0 if unstratified else int(base['tier'][i]))].append(i)
 kept=[]
 for g in groups.values():kept.extend(sorted(g,key=lambda i:-base['score'][i])[:budget])
 kept=np.asarray(sorted(kept,key=lambda i:(sequences[int(base['sequence_index'][i])],int(base['source'][i]),int(base['tier'][i]),-base['score'][i],int(base['destination'][i]))),np.int64)
 floor=np.full(len(kept),.82) if shared_floor else np.asarray([.82,.84,.86,.88,.90])[base['tier'][kept]];a=base['sim_max'][kept]>=floor;b=base['sim_topk_mean'][kept]>=floor-.025
 ok=a&b if gate=='dual' else a if gate=='maximum' else b if gate=='topthree' else np.ones(len(kept),bool)
 if max_gap is not None:ok&=base['gap_seconds'][kept]<max_gap
 pos=kept[ok];g={k:base[k][pos] for k in ['edge_id','sequence_index','source','destination','score']};return g,kept,pos

def build(config):
 allowed={'carrier_root','sequences','minimum_observations','embedding_cache','embedding_keys','fps_by_sequence'};assert set(config)==allowed
 t=time.perf_counter();tracks,counts=read_tracks(config['carrier_root'],config['sequences'],config['minimum_observations']);a=time.perf_counter();stats=attach_cached_features(tracks,config['embedding_cache'],config['embedding_keys']);b=time.perf_counter();base=score_all(tracks,config['sequences'],config['fps_by_sequence']);c=time.perf_counter();g,kept,pos=sparse_qualify(base,config['sequences']);d=time.perf_counter()
 return g,base,stats,{'carrier_read_tracklets_seconds':a-t,'feature_load_prototypes_seconds':b-a,'all_feasible_scoring_seconds':c-b,'candidate_sort_qualification_seconds':d-c,'frontend_seconds':d-t,'all_feasible_edges':len(base['edge_id']),'retained_candidates':len(kept),'qualified_edges':len(pos)}
