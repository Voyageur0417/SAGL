"""Check the released checkpoint, encoder loading and one image-crop forward pass."""
from pathlib import Path
import sys,argparse,json,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--checkpoint',required=True);ap.add_argument('--device',default='cpu');ap.add_argument('--crop',help='Optional real player crop; no image is downloaded');ap.add_argument('--output');a=ap.parse_args()
from sagl_repro.features import load_model,preprocess
from sagl_repro.common import sha256,dump
import torch,numpy as np
p=Path(a.checkpoint);expected='0634e9782792d27ff066e3c20f6c00a93d7bb662c51a4976e39eae2bf36507f9'
if sha256(p)!=expected:raise ValueError('Wrong original checkpoint SHA256')
model,meta=load_model(p,a.device)
if a.crop:
 import cv2
 image=cv2.imread(a.crop,cv2.IMREAD_COLOR)
 if image is None:raise ValueError('Cannot read crop')
 rgb=cv2.resize(cv2.cvtColor(image,cv2.COLOR_BGR2RGB),(128,256),interpolation=cv2.INTER_LINEAR);source='user_supplied_real_crop'
else:rgb=np.zeros((256,128,3),np.uint8);source='black_shape_probe_not_a_reproduction_result'
x=torch.from_numpy(np.ascontiguousarray(preprocess(rgb)[None])).to(a.device)
with torch.no_grad():f=model(x);normalized=torch.nn.functional.normalize(f,dim=1)
assert tuple(f.shape)==(1,512) and bool(torch.isfinite(f).all())
r={'checkpoint_SHA256':expected,'bytes':p.stat().st_size,'model':meta,'device':a.device,'input_shape':list(x.shape),'output_shape':list(f.shape),'input_source':source,'output_finite':True,'normalized_feature_norm':float(torch.linalg.vector_norm(normalized).item()),'GT_read':False,'torch':torch.__version__}
if a.output:dump(a.output,r)
print(json.dumps(r,indent=2))
