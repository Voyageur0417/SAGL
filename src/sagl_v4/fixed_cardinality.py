"""Exact cardinality assignment; adapted from the previously exhaustively verified solver.
No truncation, GT or baseline-result access. Negative weights are legal at fixed k.
"""
import time
import numpy as np
from scipy.optimize import linear_sum_assignment

def solve_exact(ns,nd,pairs,weights,k):
    assert 0<=k<=min(ns,nd)
    if k==0:return [],0.,{'prepare_seconds':0.,'solver_seconds':0.,'matrix_bytes':0}
    t=time.perf_counter();n=ns+nd-k;mat=np.full((n,n),-1e6,dtype=np.float64);mat[:ns,nd:]=0.;mat[ns:,:nd]=0.;mapping={}
    for i,((s,d),w) in enumerate(zip(pairs,weights)):
        s=int(s);d=int(d);assert (s,d) not in mapping and np.isfinite(w);mat[s,d]=w;mapping[s,d]=i
    prepare=time.perf_counter()-t;t=time.perf_counter();rr,cc=linear_sum_assignment(mat,maximize=True);elapsed=time.perf_counter()-t
    assert (mat[rr,cc]>-1e5).all(),'infeasible requested k'
    ids=[mapping[int(r),int(c)] for r,c in zip(rr,cc) if r<ns and c<nd];assert len(ids)==k
    return ids,float(np.asarray(weights)[ids].sum()),{'prepare_seconds':prepare,'solver_seconds':elapsed,'matrix_bytes':int(mat.nbytes)}

def select_exact_graph(graph,weights,counts):
    chosen=[];prepare=solve=0.;peak=0
    for seq in np.unique(graph['sequence_index']):
        pos=np.flatnonzero(graph['sequence_index']==seq);src=np.unique(graph['source'][pos]);dst=np.unique(graph['destination'][pos]);pairs=list(zip(np.searchsorted(src,graph['source'][pos]),np.searchsorted(dst,graph['destination'][pos])));ids,obj,st=solve_exact(len(src),len(dst),pairs,weights[pos],int(counts[int(seq)]));chosen.extend(pos[ids].tolist());prepare+=st['prepare_seconds'];solve+=st['solver_seconds'];peak=max(peak,st['matrix_bytes'])
    chosen=np.asarray(sorted(chosen,key=lambda i:(-graph['score'][i],i)),np.int64)
    return chosen,{'stage2_matrix_preparation_seconds':prepare,'stage2_matching_seconds':solve,'stage2_max_matrix_bytes':peak}
