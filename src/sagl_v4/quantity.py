"""Compute quantities now, using P; never load historical counts."""
import time
import numpy as np
from .core import match_graph

def quantity_from_p(graph,lambda0=.84):
    t=time.perf_counter();net=graph['score']-lambda0;weight_time=time.perf_counter()-t;t=time.perf_counter();selected,st=match_graph(graph,net);counts={int(s):int((graph['sequence_index'][selected]==s).sum()) for s in np.unique(graph['sequence_index'])};elapsed=time.perf_counter()-t
    return selected,counts,{'quantity_weight_seconds':weight_time,'quantity_total_seconds':elapsed,'stage1_matrix_preparation_seconds':st['matrix_preparation_seconds'],'stage1_matching_seconds':st['matching_solver_seconds'],'stage1_max_matrix_bytes':st['max_matrix_bytes']}
