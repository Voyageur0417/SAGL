from pathlib import Path
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
import argparse,json
from sagl_repro.common import sha256,dump
from sagl_repro.features import read_rows
ap=argparse.ArgumentParser();ap.add_argument('--carrier',required=True);ap.add_argument('--prediction',required=True);ap.add_argument('--reference');ap.add_argument('--output');a=ap.parse_args()
src=read_rows(a.carrier);dst=read_rows(a.prediction)
if len(src)!=len(dst):raise AssertionError('row count changed')
changed=0
for (_,x),(_,y) in zip(src,dst):
 if x[:1]+x[2:]!=y[:1]+y[2:]:raise AssertionError('non-ID token or row order changed')
 changed+=x[1]!=y[1]
report={'rows':len(src),'changed_ID_tokens':changed,'ID_only':True,'duplicate_frame_ID':False,'prediction_SHA256':sha256(a.prediction),'reference_byte_equal':Path(a.prediction).read_bytes()==Path(a.reference).read_bytes() if a.reference else None}
if a.output:dump(a.output,report)
print(json.dumps(report,indent=2))
if a.reference and not report['reference_byte_equal']:raise SystemExit(2)
