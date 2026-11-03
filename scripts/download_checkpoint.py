"""Download the original released Sports-ReID checkpoint and verify its exact identity."""
from pathlib import Path
import argparse,hashlib,urllib.request,json,os
URL='https://github.com/Voyageur0417/SAGL/releases/download/v1.0.0/clean_sportsmot_train_only_osnet_x1_0_epoch60.pth'
SHA256='0634e9782792d27ff066e3c20f6c00a93d7bb662c51a4976e39eae2bf36507f9'
SIZE=30535806
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--output',default='checkpoint/clean_sportsmot_train_only_osnet_x1_0_epoch60.pth');a=ap.parse_args();out=Path(a.output).resolve()
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
if out.exists():
 if out.stat().st_size!=SIZE or digest(out)!=SHA256:raise SystemExit('Existing file differs; refusing to overwrite it.')
 print(json.dumps({'file':str(out),'SHA256':SHA256,'verified':True,'downloaded':False}));raise SystemExit(0)
out.parent.mkdir(parents=True,exist_ok=True);tmp=out.with_suffix(out.suffix+'.part')
if tmp.exists():raise SystemExit('Partial download already exists; inspect/remove it before retrying.')
try:
 req=urllib.request.Request(URL,headers={'User-Agent':'SAGL-v1.0.0-checkpoint-download'})
 with urllib.request.urlopen(req,timeout=60) as src,tmp.open('xb') as dst:
  while True:
   data=src.read(1024*1024)
   if not data:break
   dst.write(data)
 if tmp.stat().st_size!=SIZE or digest(tmp)!=SHA256:raise ValueError('Checkpoint size or SHA256 verification failed')
 os.replace(tmp,out)
except BaseException:
 tmp.unlink(missing_ok=True);raise
print(json.dumps({'file':str(out),'SHA256':SHA256,'verified':True,'downloaded':True,'url':URL}))
