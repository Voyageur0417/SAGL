import math,time
import numpy as np
from .quantity import quantity_from_p
from .competition_details import extract_competition
from .chain_compatibility import chain_compatibility
from .fixed_cardinality import select_exact_graph

def decide_decoupled(graph,config):
    assert set(config)<={'name','method','lambda','delta','beta'},'external quantities/labels not accepted'
    method=config['method'];lam=float(config.get('lambda',.84));delta=float(config.get('delta',.03));beta=float(config.get('beta',.02));assert lam>=0 and delta>0 and beta>=0
    pidx,counts,timings=quantity_from_p(graph,lam);comp=None;timings.update(competition_seconds=0.,chain_compatibility_seconds=0.,selection_weight_seconds=0.,chain_index_shallow_bytes=0,compatibility_array_bytes=0)
    if method in ['v4_c1','v4_c2']:
        t=time.perf_counter();comp=extract_competition(graph,delta);timings['competition_seconds']=time.perf_counter()-t
        if method=='v4_c2':
            t=time.perf_counter();h,mem=chain_compatibility(graph,comp);comp.update(h);timings.update(mem);timings['chain_compatibility_seconds']=time.perf_counter()-t;A=comp['ambiguity_c2']
        else:A=comp['ambiguity_b1']
    t=time.perf_counter();weight=graph['score'].copy()
    if comp is not None:weight=weight-beta*A
    timings['selection_weight_seconds']=time.perf_counter()-t;t=time.perf_counter();selected,st=select_exact_graph(graph,weight,counts);timings.update(st);timings['selection_total_seconds']=time.perf_counter()-t;timings['max_matrix_bytes']=max(st['stage2_max_matrix_bytes'],timings['stage1_max_matrix_bytes']);audit=[]
    for sq,k in counts.items():
        a=pidx[graph['sequence_index'][pidx]==sq];b=selected[graph['sequence_index'][selected]==sq];assert len(a)==len(b)==k
        rawp=math.fsum(map(float,graph['score'][a]));raw2=math.fsum(map(float,graph['score'][b]));wp=math.fsum(map(float,weight[a]));ws=math.fsum(map(float,weight[b]));assert ws>=wp-1e-9;audit.append({'sequence_index':sq,'K_current_P':k,'stage2_count':len(b),'P_raw_score_sum':rawp,'stage2_raw_score_sum':raw2,'P_net_objective':math.fsum(map(float,graph['score'][a]-lam)),'stage2_selection_weight_sum':ws,'P_selection_weight_sum':wp,'selection_objective_delta_vs_P':ws-wp,'raw_objective_delta':raw2-rawp,'same_edges_as_P':set(map(int,a))==set(map(int,b))})
        if method=='v4_c0':assert abs(raw2-rawp)<1e-9,'C0/P objective mismatch'
    return {'selected_positions':selected,'accepted_edge_id':graph['edge_id'][selected],'utility':weight,'competition':comp,'timings':timings,'quantity_stage':audit,'quantity_accepted_edge_id':graph['edge_id'][pidx]}
