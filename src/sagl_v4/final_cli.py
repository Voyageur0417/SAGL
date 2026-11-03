"""Final SAGL entry: carrier + frozen observations + frontend config -> ID-only prediction."""
import argparse,json,time
from pathlib import Path
import numpy as np
from .final_frontend import build
from .core import decide
from .projection import links_to_id_map,write_id_projection_file

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input',required=True);ap.add_argument('--output',required=True);args=ap.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=False);cfg=json.loads(Path(args.input).read_text());start=time.perf_counter();g,base,stats,timing=build(cfg);r=decide(g,{'method':'v4_c1','lambda':.84,'beta':.02,'delta':.03});links=[{'sequence':cfg['sequences'][int(g['sequence_index'][i])],'src':int(g['source'][i]),'dst':int(g['destination'][i]),'edge_id':int(g['edge_id'][i]),'score':float(g['score'][i])} for i in r['selected_positions']];maps=links_to_id_map(links)
 for seq in cfg['sequences']:write_id_projection_file(Path(cfg['carrier_root'])/(seq+'.txt'),out/'tracker/data'/(seq+'.txt'),maps.get(seq,{}))
 np.savez_compressed(out/'qualified_graph.npz',**g);np.savez_compressed(out/'edge_sets.npz',accepted=r['accepted_edge_id'],current_P=r['quantity_accepted_edge_id']);(out/'id_map.json').write_text(json.dumps(maps,indent=2)+'\n');(out/'runtime.json').write_text(json.dumps({**timing,**r['timings'],'full_cached_feature_postprocess_seconds':time.perf_counter()-start,'includes_ReID_extraction':False,'GT_read':False},indent=2)+'\n');(out/'quantity_stage.json').write_text(json.dumps(r['quantity_stage'],indent=2)+'\n')
if __name__=='__main__':main()
