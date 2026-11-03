"""Directed structural witnesses; no GT or chosen links are consulted."""
import sys
import numpy as np

def chain_compatibility(graph,competition):
    index={(int(s),int(u),int(v)):i for i,(s,u,v) in enumerate(zip(graph['sequence_index'],graph['source'],graph['destination']))};n=len(graph['score']);out={}
    for side in ['source','destination']:
        witness=np.full(n,-1,np.int64)
        for i in np.flatnonzero(competition[side+'_exists']):
            k=int(competition[side+'_competitor_endpoint'][i]);s=int(graph['sequence_index'][i]);u=int(graph['source'][i]);v=int(graph['destination'][i]);key=(s,v,k) if side=='source' else (s,k,u);witness[i]=index.get(key,-1)
        valid=witness>=0;ids=np.full(n,-1,np.int64);ids[valid]=graph['edge_id'][witness[valid]];out[side+'_witness_position']=witness;out[side+'_witness_edge_id']=ids;out['h_'+side]=valid;out['corrected_'+side+'_ambiguity']=competition[side+'_ambiguity']*(~valid)
    out['ambiguity_c2']=np.maximum(out['corrected_source_ambiguity'],out['corrected_destination_ambiguity']);return out,{'chain_index_shallow_bytes':sys.getsizeof(index),'compatibility_array_bytes':sum(v.nbytes for v in out.values()),'qualified_index_entries':len(index)}
