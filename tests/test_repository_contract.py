"""Release contracts; these do not retune or replace the frozen algorithm."""
from pathlib import Path
import json,hashlib,math,unittest,sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from sagl_repro.common import load_config
class RepositoryContracts(unittest.TestCase):
 def test_frozen_implementation_bytes(self):
  records=json.loads((ROOT/'manifests/frozen_source_manifest.json').read_text())
  for x in records:self.assertEqual(hashlib.sha256((ROOT/x['file']).read_bytes()).hexdigest(),x['package_sha256'],x['file'])
 def test_full_protocol_configurations(self):
  for name,n in [('sportsmot_ocsort.yaml',45),('sportsmot_diffmot.yaml',45),('soccernet.yaml',20),('teamtrack.yaml',45)]:
   c=load_config(ROOT/'configs'/name);self.assertEqual(len(c['sequences']),n);self.assertTrue(all(math.isfinite(float(s['fps'])) and float(s['fps'])>0 for s in c['sequences']))
 def test_vendored_trackeval_snapshot_complete(self):
  records=json.loads((ROOT/'manifests/trackeval_source_manifest.json').read_text())['files']
  for x in records:self.assertEqual(hashlib.sha256((ROOT/'vendor/trackeval'/x['file']).read_bytes()).hexdigest(),x['SHA256'],x['file'])
 def test_third_party_licences_retained(self):
  for name,author in [('OSNET_MIT_LICENSE.txt','Kaiyang Zhou'),('TRACKEVAL_LICENSE.txt','Jonathon Luiten')]:
   s=(ROOT/'vendor'/name).read_text();self.assertIn('MIT License',s);self.assertIn(author,s)
 def test_citation_has_no_invented_publication_identifiers(self):
  import yaml
  c=yaml.safe_load((ROOT/'CITATION.cff').read_text());self.assertEqual([a['family-names'] for a in c['authors']],['Hu','Han','Su','Hao']);self.assertNotIn('doi',c);self.assertEqual(c['repository-code'],'https://github.com/Voyageur0417/SAGL')
if __name__=='__main__':unittest.main()
