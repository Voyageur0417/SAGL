"""Create an author-generated format example, NOT sports data or a benchmark."""
from pathlib import Path
import argparse,json
import numpy as np
ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);a=ap.parse_args();r=Path(a.output);r.mkdir(parents=True,exist_ok=False);(r/'carrier').mkdir();(r/'cache').mkdir();rows=[];keys=[]
for tid,frames in [(10,[1,2]),(20,[5,6]),(30,[9,10])]:
 for i,frame in enumerate(frames):
  rows.append(f'{frame},{tid},10,20,30,60,0.9,-1,-1,-1\n');keys.append({'sequence':'toy','tid':tid,'local_index':i,'frame':frame,'score':.9,'area':1800.})
(r/'carrier/toy.txt').write_text(''.join(rows));f=np.zeros((6,512),np.float16);f[:,0]=1;np.save(r/'cache/features.npy',f);(r/'cache/features.keys.json').write_text(json.dumps(keys,indent=2));(r/'config.json').write_text(json.dumps({'dataset_profile':'sportsmot','carrier_root':'carrier','sequences':[{'name':'toy','fps':25}],'minimum_observations':2},indent=2));print(r)
