import sys,unittest,tempfile,json,itertools
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from sagl_repro.features import read_rows,collect,crop_rgb,preprocess
from sagl_repro.common import load_config
from sagl_v4.fixed_cardinality import solve_exact
from sagl_v4.core import decide,competition
from sagl_v4.projection import links_to_id_map,write_id_projection_file

class ReproductionTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
 def tearDown(self):self.tmp.cleanup()
 def cfg(self,profile,content):
  (self.root/'one.txt').write_text(content)
  return {'dataset_profile':profile,'minimum_observations':1 if profile=='teamtrack' else 2,'carrier_root':str(self.root),'sequences':[{'name':'one','fps':25}]}
 def test_track_mapping_and_eligibility(self):
  c=self.cfg('sportsmot','3,9,0,0,4,4,.8\n1,9,1,1,4,4,.9\n2,7,1,1,4,4,.5\n');k,_,obs=collect(c)
  self.assertEqual([x['frame'] for x in k],[1,3]);self.assertEqual([x['row_index'] for x in obs],[0,1,2]);self.assertIsNone(obs[-1]['feature_index']);self.assertEqual(k[0]['local_index'],0)
 def test_teamtrack_original_row_order_no_area(self):
  c=self.cfg('teamtrack','3,9,0,0,4,4,.8\n1,9,1,1,4,4,.9\n2,7,1,1,4,4,.5\n');k,_,_=collect(c)
  self.assertEqual([x['row_index'] for x in k],[0,1,2]);self.assertTrue(all('area' not in x for x in k))
 def test_duplicate_frame_identity_rejected(self):
  self.cfg('sportsmot','1,1,0,0,2,2,.5\n1,1,0,0,2,2,.5\n')
  with self.assertRaises(ValueError):read_rows(self.root/'one.txt')
 def test_nonfinite_rejected(self):
  self.cfg('sportsmot','1,1,nan,0,2,2,.5\n')
  with self.assertRaises(ValueError):read_rows(self.root/'one.txt')
 def test_crop_floor_ceil_clamp(self):
  row=['1','1','-1.2','1.2','4.8','3.1','.7'];im=np.zeros((5,6,3),np.uint8);im[:,:,2]=255
  x,meta=crop_rgb(im,row,'sportsmot');self.assertEqual(meta['bounds'],[0,1,4,5]);self.assertEqual(x.shape,(256,128,3));self.assertTrue(np.all(x[:,:,0]==255))
 def test_missing_image_profiles(self):
  row=['1','1','1','1','2','2','.5'];a,_=crop_rgb(None,row,'sportsmot');b,_=crop_rgb(None,row,'teamtrack')
  self.assertTrue(np.all(a==0));self.assertIsNone(b)
 def test_teamtrack_invalid_zero_feature(self):
  row=['1','1','1','1','1','4','.5'];a,meta=crop_rgb(np.zeros((9,9,3),np.uint8),row,'teamtrack');self.assertIsNone(a)
 def test_preprocess_dtype_shape(self):
  x=preprocess(np.zeros((256,128,3),np.uint8));self.assertEqual(x.dtype,np.float32);self.assertEqual(x.shape,(3,256,128));self.assertAlmostEqual(float(x[0,0,0]),-.485/.229,places=6)
 def test_projection_non_ID_and_chain(self):
  source=self.root/'source.txt';dest=self.root/'out.txt';source.write_text('1,8,1.00,2,3,4,0.5,-1\n2,9,3,4,5,6,.6,-1\n3,10,3,4,5,6,.6,-1\n')
  m=links_to_id_map([{'sequence':'one','src':8,'dst':9},{'sequence':'one','src':9,'dst':10}]);write_id_projection_file(source,dest,m['one']);a=read_rows(source);b=read_rows(dest)
  self.assertTrue(all(x[:1]+x[2:]==y[:1]+y[2:] for (_,x),(_,y) in zip(a,b)));self.assertEqual({int(float(y[1])) for _,y in b},{8})
 def test_cardinality_exhaustive(self):
  rng=np.random.default_rng(42)
  for repeat in range(30):
   pairs=[(i,j) for i in range(3) for j in range(3) if rng.random()<.7];w=rng.uniform(-.2,1,len(pairs))
   for k in range(4):
    possible=[inds for inds in itertools.combinations(range(len(pairs)),k) if len({pairs[x][0] for x in inds})==k and len({pairs[x][1] for x in inds})==k]
    if not possible:
     with self.assertRaises(AssertionError):solve_exact(3,3,pairs,w,k)
    else:
     ids,obj,_=solve_exact(3,3,pairs,w,k);best=max(sum(w[x] for x in inds) for inds in possible);self.assertEqual(len(ids),k);self.assertAlmostEqual(obj,best,places=12)
 def test_no_competitor_and_sequence_isolation(self):
  g={'edge_id':np.array([0,1]),'sequence_index':np.array([0,1]),'source':np.array([1,1]),'destination':np.array([2,2]),'score':np.array([.9,.88])};self.assertTrue(np.all(competition(g)['ambiguity_v1']==0));a=decide(g,{'method':'v4_c1','lambda':.84,'beta':.02,'delta':.03});self.assertEqual(len(a['accepted_edge_id']),2)
 def test_fixed_quantity_and_determinism(self):
  g={'edge_id':np.arange(4),'sequence_index':np.zeros(4,dtype=int),'source':np.array([1,1,2,2]),'destination':np.array([3,4,3,4]),'score':np.array([.9,.9,.9,.9])}
  outs=[decide(g,{'method':'v4_c1','lambda':.84,'beta':.02,'delta':.03}) for _ in range(3)]
  self.assertTrue(all(np.array_equal(outs[0]['accepted_edge_id'],v['accepted_edge_id']) for v in outs));self.assertEqual(len(outs[0]['accepted_edge_id']),len(outs[0]['quantity_accepted_edge_id']))
 def test_empty_graph(self):
  g={k:np.array([],dtype=float if k=='score' else int) for k in ['edge_id','sequence_index','source','destination','score']};a=decide(g,{'method':'v4_c1','lambda':.84,'beta':.02,'delta':.03});self.assertEqual(len(a['accepted_edge_id']),0)

if __name__=='__main__':unittest.main(verbosity=2)
