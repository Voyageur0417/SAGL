"""GT-free wrappers preserving the two historical observation-cache profiles."""
import math, time, json, platform, importlib.metadata
from pathlib import Path
from collections import defaultdict
import numpy as np
from .common import sha256,dump

def read_rows(path):
 rows=[]
 for line_no,line in enumerate(Path(path).read_text().splitlines(),1):
  if not line.strip():continue
  row=line.split(',')
  if len(row)<7:raise ValueError(f'{path}:{line_no}: expected >=7 MOT fields')
  vals=list(map(float,row[:7]))
  if not all(math.isfinite(v) for v in vals):raise ValueError('non-finite carrier input')
  if not vals[0].is_integer() or vals[0]<1 or not vals[1].is_integer():raise ValueError('invalid frame or identity')
  rows.append((line_no,row))
 pairs=[(int(float(v[0])),int(float(v[1]))) for _,v in rows]
 if len(pairs)!=len(set(pairs)):raise ValueError('duplicate original (frame, ID)')
 return rows

def crop_rgb(image,row,profile):
 import cv2
 if image is None:
  return (None if profile=='teamtrack' else np.zeros((256,128,3),np.uint8)),{'status':'MISSING_IMAGE','bounds':None}
 x,y,w,h=map(float,row[2:6]);ih,iw=image.shape[:2]
 if profile=='teamtrack' and not (math.isfinite(x) and math.isfinite(y) and w>1 and h>1):
  return None,{'status':'INVALID_BBOX_ZERO_FEATURE','bounds':None}
 a=max(0,min(iw-1,math.floor(x)));b=max(0,min(ih-1,math.floor(y)))
 c=max(0,min(iw,math.ceil(x+w)));d=max(0,min(ih,math.ceil(y+h)))
 bounds=[a,b,c,d]
 if c<=a or d<=b:
  return (None if profile=='teamtrack' else np.zeros((256,128,3),np.uint8)),{'status':'EMPTY_CROP_ZERO_FEATURE' if profile=='teamtrack' else 'EMPTY_CROP_BLACK_INPUT','bounds':bounds}
 crop=cv2.cvtColor(image[b:d,a:c],cv2.COLOR_BGR2RGB)
 return cv2.resize(crop,(128,256),interpolation=cv2.INTER_LINEAR),{'status':'OK','bounds':bounds,'image_size':[iw,ih]}

def preprocess(rgb):
 mean=np.asarray([.485,.456,.406],np.float32).reshape(1,1,3)
 std=np.asarray([.229,.224,.225],np.float32).reshape(1,1,3)
 return ((rgb.astype(np.float32)/255.-mean)/std).transpose(2,0,1)

def load_model(checkpoint,device):
 import torch
 from vendor.osnet import osnet_x1_0
 # Accept only trusted local checkpoints. Original pickle contains training state.
 blob=torch.load(checkpoint,map_location='cpu',weights_only=False)
 state=blob.get('state_dict',blob)
 state={k.removeprefix('module.'):v for k,v in state.items()}
 nc=int(state['classifier.weight'].shape[0]) if 'classifier.weight' in state else 1
 model=osnet_x1_0(num_classes=nc,pretrained=False,loss='triplet')
 report=model.load_state_dict(state,strict=False)
 allowed={'classifier.weight','classifier.bias'} if 'classifier.weight' not in state else set()
 if set(report.missing_keys)!=allowed or report.unexpected_keys:raise ValueError(f'incomplete encoder: {report}')
 return model.to(device).eval(),{'classifier_classes_loaded':nc if nc!=1 else None,'missing_keys':report.missing_keys,'unexpected_keys':report.unexpected_keys,'architecture':'osnet_x1_0','embedding_dimension':512}

def collect(config):
 profile=config['dataset_profile'];keys=[];items=[];observations=[]
 for seq in config['sequences']:
  name=seq['name'];rows=read_rows(Path(config['carrier_root'])/(name+'.txt'))
  counts=defaultdict(int)
  for _,v in rows:counts[int(float(v[1]))]+=1
  local=[]
  for ri,(lineno,row) in enumerate(rows):
   tid=int(float(row[1]));obs={'sequence':name,'row_index':ri,'raw_line_number':lineno,'original_carrier_id':tid,'frame':int(float(row[0])),'bbox':list(map(float,row[2:6])),'confidence':float(row[6]),'feature_index':None}
   observations.append(obs)
   if counts[tid]>=config['minimum_observations']:local.append((ri,row,obs))
  if profile!='teamtrack':local.sort(key=lambda v:(int(float(v[1][1])),int(float(v[1][0]))))
  idx_by_tid=defaultdict(int)
  for ri,row,obs in local:
   tid=int(float(row[1]));idx=idx_by_tid[tid];idx_by_tid[tid]+=1
   if profile=='teamtrack':
    x,y,w,h=map(float,row[2:6]);k={'sequence':name,'scene':name.split('__')[0],'track_id':tid,'row_index':ri,'frame':int(float(row[0])),'bbox':[x,y,w,h],'score':float(row[6]),'valid_bbox':math.isfinite(x) and math.isfinite(y) and w>1 and h>1}
   else:
    w,h=map(float,row[4:6]);k={'sequence':name,'tid':tid,'local_index':idx,'frame':int(float(row[0])),'score':float(row[6]),'area':max(0.,w)*max(0.,h)}
   obs['feature_index']=len(keys);keys.append(k);items.append((seq,row,obs))
 return keys,items,observations

def extract(config,output,device='cpu',batch_size=None):
 import torch,cv2
 from torch.nn import functional as F
 output=Path(output);output.mkdir(parents=True,exist_ok=False);t=time.perf_counter()
 profile=config['dataset_profile'];bs=batch_size or (256 if profile=='teamtrack' else 192)
 if bs<1:raise ValueError('batch_size must be positive')
 if device.startswith('cuda') and not torch.cuda.is_available():raise RuntimeError('CUDA requested but unavailable; CPU is an explicit option')
 checkpoint=Path(config['checkpoint']);cksha=sha256(checkpoint)
 if config.get('checkpoint_sha256') and cksha!=config['checkpoint_sha256']:raise ValueError('checkpoint SHA256 mismatch')
 keys,items,observations=collect(config);a=time.perf_counter();model,model_meta=load_model(checkpoint,device);b=time.perf_counter()
 feats=np.zeros((len(keys),512),np.float16);imgs=[];indices=[];batches=[];media={};cropstatus=defaultdict(int)
 def flush():
  if not imgs:return
  arr=np.stack(imgs).astype(np.float32)
  # Original Sports/SoccerNet DataLoader stacks contiguous NCHW tensors;
  # TeamTrack originally used NumPy stacking and retains its channels-last strides.
  if profile!='teamtrack':arr=np.ascontiguousarray(arr)
  tensor=torch.from_numpy(arr).to(device,non_blocking=True)
  with torch.no_grad():v=F.normalize(model(tensor),dim=1).cpu().numpy().astype(np.float16)
  if not np.isfinite(v).all():raise ValueError('non-finite embedding')
  feats[np.asarray(indices,np.int64)]=v;batches.append({'batch':len(batches),'count':len(indices),'first_feature_index':indices[0],'last_feature_index':indices[-1]});imgs.clear();indices.clear()
 def add(image,row,obs):
  rgb,meta=crop_rgb(image,row,profile);obs.update(meta);cropstatus[meta['status']]+=1
  if rgb is not None:
   imgs.append(preprocess(rgb));indices.append(obs['feature_index'])
   if len(imgs)>=bs:flush()
 if profile!='teamtrack':
  for number,(seq,row,obs) in enumerate(items):
   frame=int(float(row[0]));path=Path(seq['images'])/(f'{frame:06d}.jpg')
   if not path.exists():path=Path(seq['images'])/(f'{frame:08d}.jpg')
   if str(path) not in media:media[str(path)]={'exists':path.exists(),'SHA256':sha256(path) if path.exists() else None}
   image=cv2.imread(str(path),cv2.IMREAD_COLOR);add(image,row,obs)
   if number%5000==0:print(f'features {number}/{len(items)}',flush=True)
  flush()
 else:
  for seq in config['sequences']:
   path=Path(seq['video']);media[str(path)]={'exists':path.exists(),'SHA256':sha256(path) if path.exists() else None};cap=cv2.VideoCapture(str(path))
   if not cap.isOpened():raise RuntimeError(f'cannot open video {path}')
   meta={'width':cap.get(cv2.CAP_PROP_FRAME_WIDTH),'height':cap.get(cv2.CAP_PROP_FRAME_HEIGHT),'container_fps':cap.get(cv2.CAP_PROP_FPS),'reported_frames':cap.get(cv2.CAP_PROP_FRAME_COUNT),'protocol_fps':seq['fps']};byframe=defaultdict(list)
   for ss,row,obs in items:
    if ss['name']==seq['name']:byframe[int(float(row[0]))].append((row,obs))
   frame=0
   while True:
    ok,image=cap.read()
    if not ok:break
    frame+=1
    for row,obs in byframe.get(frame,[]):add(image,row,obs)
   cap.release();flush();meta['decoded_frames']=frame;media[str(path)].update(meta)
   for fr,rr in byframe.items():
    if fr>frame:
     for _,obs in rr:obs.update({'status':'MISSING_VIDEO_FRAME_ZERO_FEATURE','bounds':None});cropstatus['MISSING_VIDEO_FRAME_ZERO_FEATURE']+=1
 c=time.perf_counter();np.save(output/'features.npy',feats);dump(output/'features.keys.json',keys);dump(output/'observation_manifest.json',observations)
 dump(output/'extraction_manifest.json',{'profile':profile,'checkpoint_SHA256':cksha,'model':model_meta,'device':device,'batch_size':bs,'cache_dtype':str(feats.dtype),'shape':list(feats.shape),'normalization':'torch.nn.functional.normalize dim=1 eps=1e-12, then float16; no AMP','GT_read':False,'minimum_observations':config['minimum_observations'],'counts':dict(cropstatus),'media':media,'carrier_SHA256':{s['name']:sha256(Path(config['carrier_root'])/(s['name']+'.txt')) for s in config['sequences']},'batch_layout':batches,'timings':{'mapping_seconds':a-t,'model_load_seconds':b-a,'decode_preprocess_forward_seconds':c-b,'total_seconds':time.perf_counter()-t},'environment':{'python':platform.python_version(),'numpy':np.__version__,'torch':torch.__version__,'opencv':cv2.__version__,'CUDA_built':torch.version.cuda,'cudnn':torch.backends.cudnn.version(),'cudnn_benchmark':torch.backends.cudnn.benchmark,'cudnn_deterministic':torch.backends.cudnn.deterministic,'cuda_matmul_allow_tf32':torch.backends.cuda.matmul.allow_tf32,'cudnn_allow_tf32':torch.backends.cudnn.allow_tf32,'gpu':torch.cuda.get_device_name(torch.device(device)) if device.startswith('cuda') else None}})
 print(f'completed {profile}: {feats.shape}, {time.perf_counter()-t:.2f}s',flush=True)
