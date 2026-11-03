from pathlib import Path
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
import json,platform,importlib,os
info={'python':platform.python_version(),'executable':sys.executable,'platform':platform.platform(),'PYTHONNOUSERSITE':os.environ.get('PYTHONNOUSERSITE'),'packages':{}}
for name in ['numpy','scipy','cv2','PIL','yaml','torch','torchvision']:
 try:
  m=importlib.import_module(name);info['packages'][name]={'version':str(m.__version__),'location':m.__file__}
 except Exception as e:info['packages'][name]={'error':str(e)}
try:
 import torch
 info['CUDA_built']=torch.version.cuda;info['cuda_available']=torch.cuda.is_available();info['gpu']=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())];info['cudnn']=torch.backends.cudnn.version()
except Exception as e:info['CUDA_probe_error']=str(e)
print(json.dumps(info,indent=2))
