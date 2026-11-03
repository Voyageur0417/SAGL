from pathlib import Path
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
import argparse
from sagl_repro.common import load_config
from sagl_repro.features import extract
ap=argparse.ArgumentParser(description='GT-free frozen Sports-ReID observation embeddings')
ap.add_argument('--config',required=True);ap.add_argument('--output',required=True);ap.add_argument('--checkpoint');ap.add_argument('--device',default='cpu');ap.add_argument('--batch-size',type=int)
a=ap.parse_args();c=load_config(a.config)
if a.checkpoint:c['checkpoint']=str(Path(a.checkpoint).resolve())
# Input-presence validation only; per-observation fallbacks remain the original protocol.
if not Path(c['carrier_root']).is_dir():raise FileNotFoundError('carrier_root does not exist')
if not Path(c['checkpoint']).is_file():raise FileNotFoundError('checkpoint does not exist')
for seq in c['sequences']:
 key='video' if c['dataset_profile']=='teamtrack' else 'images'
 if key not in seq or not Path(seq[key]).exists():raise FileNotFoundError(f'media path missing for {seq["name"]}')
extract(c,a.output,a.device,a.batch_size)
