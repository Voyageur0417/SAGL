"""Inference only: no GT, evaluation results, baseline counts or dataset-specific rules."""
import time
import numpy as np
from scipy.optimize import linear_sum_assignment

def _direction(seq, node, score):
    n=len(score)
    if not n:return dict(competitor=np.empty(0),exists=np.empty(0,bool),margin=np.empty(0),rank=np.empty(0,np.int32))
    order=np.lexsort((np.arange(n),-score,node,seq));s=seq[order];t=node[order]
    starts=np.flatnonzero(np.r_[True,(s[1:]!=s[:-1])|(t[1:]!=t[:-1])]);ends=np.r_[starts[1:],n];counts=ends-starts;offset=np.repeat(starts,counts);r=np.arange(n)-offset
    best=score[order[offset]];second=score[order[np.repeat(starts+np.minimum(1,counts-1),counts)]];valid=np.repeat(counts>1,counts);c=np.where(r==0,second,best);c[~valid]=np.nan;m=score[order]-c
    out={}
    for key,values in [('competitor',c),('exists',valid),('margin',m),('rank',r+1)]:
        z=np.empty_like(values);z[order]=values;out[key]=z
    return out

def competition(graph,delta=.03):
    assert delta>0
    seq=graph['sequence_index'];score=graph['score'];n=len(score)
    src=_direction(seq,graph['source'],score);dst=_direction(seq,graph['destination'],score)
    ambiguities=[]
    for d in [src,dst]:
        z=np.zeros(n);v=d['exists'];z[v]=np.clip(1-np.maximum(d['margin'][v],0)/delta,0,1);ambiguities.append(z)
    mutual=(~src['exists']|(src['margin']>=0))&(~dst['exists']|(dst['margin']>=0))
    strict=(~src['exists']|(src['margin']>0))&(~dst['exists']|(dst['margin']>0))
    return {'source_competitor':src['competitor'],'destination_competitor':dst['competitor'],'has_source_competitor':src['exists'],'has_destination_competitor':dst['exists'],'source_margin':src['margin'],'destination_margin':dst['margin'],'source_rank':src['rank'],'destination_rank':dst['rank'],'source_ambiguity':ambiguities[0],'destination_ambiguity':ambiguities[1],'ambiguity_v1':np.maximum(*ambiguities),'mutual_best_ties_allowed':mutual,'strict_mutual_best':strict}

def match_graph(graph,utility):
    selected=[];matrix_bytes=0;prepare=solver=0.
    for seq in np.unique(graph['sequence_index']):
        t=time.perf_counter();ids=np.flatnonzero(graph['sequence_index']==seq);src=graph['source'][ids];dst=graph['destination'][ids];su=np.unique(src);du=np.unique(dst);si=np.searchsorted(su,src);di=np.searchsorted(du,dst)
        mat=np.full((len(su),len(du)+len(su)),-1e6,dtype=np.float64);mat[:,len(du):]=0;mat[si,di]=utility[ids];prepare+=time.perf_counter()-t;matrix_bytes=max(matrix_bytes,mat.nbytes);t=time.perf_counter();rr,cc=linear_sum_assignment(mat,maximize=True);solver+=time.perf_counter()-t;lookup={(int(s),int(d)):int(i) for s,d,i in zip(si,di,ids)}
        selected.extend(lookup[int(r),int(c)] for r,c in zip(rr,cc) if (int(r),int(c)) in lookup and utility[lookup[int(r),int(c)]]>0)
    return np.asarray(sorted(selected,key=lambda i:(-graph['score'][i],i)),np.int64),{'matrix_preparation_seconds':prepare,'matching_solver_seconds':solver,'max_matrix_bytes':int(matrix_bytes)}

def decide(graph,config):
    assert set(graph)=={'edge_id','sequence_index','source','destination','score'}
    score=np.asarray(graph['score'],dtype=np.float64);assert np.isfinite(score).all();n=len(score)
    assert len(set(zip(graph['sequence_index'],graph['source'],graph['destination'])))==n
    if config['method'] in ['v4_c0','v4_c1','v4_c2']:
        from .decoupled import decide_decoupled
        return decide_decoupled(graph,config)
    config=dict(config);config['method']={'v4_b1':'competition_v1','v4_b2':'competition_v2'}.get(config['method'],config['method'])
    method=config['method'];lam=float(config.get('lambda',.84));beta=float(config.get('beta',0));assert beta>=0 and lam>=0
    timings={'competition_seconds':0.,'utility_seconds':0.,'greedy_seconds':0.,'matrix_preparation_seconds':0.,'matching_solver_seconds':0.,'max_matrix_bytes':0};comp=None
    if method in ['competition_v1','competition_v2']:
        t=time.perf_counter();comp=competition(graph,float(config.get('delta',.03)));comp['applied_ambiguity']=comp['ambiguity_v1'] if method=='competition_v1' else np.minimum(comp['source_ambiguity'],comp['destination_ambiguity']);timings['competition_seconds']=time.perf_counter()-t
    t=time.perf_counter();utility=score.copy() if method=='v3_greedy' else score-lam
    if comp is not None:utility=utility-beta*comp['applied_ambiguity']
    timings['utility_seconds']=time.perf_counter()-t
    if method in ['v3_greedy','threshold_greedy']:
        t=time.perf_counter();used_s=set();used_d=set();selected=[]
        for i in np.argsort(-score,kind='stable'):
            if method=='threshold_greedy' and utility[i]<=0:continue
            s=(int(graph['sequence_index'][i]),int(graph['source'][i]));d=(int(graph['sequence_index'][i]),int(graph['destination'][i]))
            if s in used_s or d in used_d:continue
            used_s.add(s);used_d.add(d);selected.append(int(i))
        selected=np.asarray(selected,np.int64);timings['greedy_seconds']=time.perf_counter()-t
    elif method in ['penalized_matching','competition_v1','competition_v2']:
        selected,st=match_graph(graph,utility);timings.update(st)
    else:raise ValueError('unsupported inference method: '+method)
    return {'selected_positions':selected,'accepted_edge_id':graph['edge_id'][selected],'utility':utility,'competition':comp,'timings':timings}
