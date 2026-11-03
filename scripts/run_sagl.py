from pathlib import Path
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
import argparse,json,time
import numpy as np
from sagl_repro.common import load_config,dump,sha256
from sagl_v4.final_frontend import build,sparse_qualify
from sagl_v4.core import decide
from sagl_v4.projection import links_to_id_map,write_id_projection_file
ap=argparse.ArgumentParser(description='Frozen final SAGL only: lambda=.84 beta=.02 delta=.03')
ap.add_argument('--config',required=True);ap.add_argument('--cache-dir');ap.add_argument('--output',required=True)
a=ap.parse_args();c=load_config(a.config);out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
cache=Path(a.cache_dir).resolve() if a.cache_dir else None
cfg={'carrier_root':c['carrier_root'],'sequences':[s['name'] for s in c['sequences']],'minimum_observations':c['minimum_observations'],'embedding_cache':str(cache/'features.npy') if cache else c['embedding_cache'],'embedding_keys':str(cache/'features.keys.json') if cache else c['embedding_keys'],'fps_by_sequence':{s['name']:s['fps'] for s in c['sequences']}}
t=time.perf_counter();g,base,stats,timing=build(cfg)
r=decide(g,{'method':'v4_c1','lambda':.84,'beta':.02,'delta':.03})
links=[{'sequence':cfg['sequences'][int(g['sequence_index'][i])],'src':int(g['source'][i]),'dst':int(g['destination'][i]),'edge_id':int(g['edge_id'][i]),'score':float(g['score'][i])} for i in r['selected_positions']]
maps=links_to_id_map(links)
for seq in cfg['sequences']:write_id_projection_file(Path(cfg['carrier_root'])/(seq+'.txt'),out/'tracker/data'/(seq+'.txt'),maps.get(seq,{}))
np.savez_compressed(out/'qualified_graph.npz',**g);np.savez_compressed(out/'all_feasible_scores.npz',**base)
np.savez_compressed(out/'edge_sets.npz',accepted=r['accepted_edge_id'],current_P=r['quantity_accepted_edge_id'])
dump(out/'id_map.json',maps);dump(out/'prototype_statistics.json',stats);dump(out/'quantity_stage.json',r['quantity_stage']);dump(out/'runtime.json',{**timing,**r['timings'],'full_cached_feature_postprocess_seconds':time.perf_counter()-t,'includes_ReID_extraction':False,'GT_read':False})
dump(out/'input_manifest.json',{'frozen_algorithm_commit':'f4db30b3a5aefb147867f7e141402a9de30b480b','parameters':{'lambda':.84,'beta':.02,'delta':.03},'config':cfg,'input_SHA256':{key:sha256(cfg[key]) for key in ('embedding_cache','embedding_keys')},'carrier_SHA256':{s:sha256(Path(cfg['carrier_root'])/(s+'.txt')) for s in cfg['sequences']}})
print(json.dumps({'accepted_links':len(links),'output':str(out)}))

# Diagnostic exports only: unchanged frozen build and decision have completed.
_,candidate_positions,qualified_positions=sparse_qualify(base,cfg['sequences'])
np.savez_compressed(out/'candidate_graph.npz',**{k:v[candidate_positions] for k,v in base.items()})
np.savez_compressed(out/'selection_details.npz',selection_weight=r['utility'],selected_positions=r['selected_positions'],**{k:v for k,v in (r.get('competition') or {}).items() if isinstance(v,np.ndarray)})
dump(out/'accepted_links.json',links)
# Include unchanged observations as singleton identity chains for complete accounting.
from collections import defaultdict
chains={}
for seq in cfg['sequences']:
    ids={int(float(line.split(',')[1])) for line in (Path(cfg['carrier_root'])/(seq+'.txt')).read_text().splitlines() if line.strip()}
    grouped=defaultdict(list)
    for tid in sorted(ids):grouped[int(maps.get(seq,{}).get(tid,tid))].append(tid)
    chains[seq]=dict(grouped)
dump(out/'identity_chains.json',chains)
dump(out/'output_manifest.json',{'qualified_graph_SHA256':sha256(out/'qualified_graph.npz'),'all_feasible_graph_SHA256':sha256(out/'all_feasible_scores.npz'),'prediction_SHA256':{seq:sha256(out/'tracker/data'/(seq+'.txt')) for seq in cfg['sequences']},'stage1_K_equals_accepted':all(x['K_current_P']==x['stage2_count'] for x in r['quantity_stage'])})
