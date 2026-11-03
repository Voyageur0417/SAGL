"""Stable strongest OTHER competitors on the frozen qualified graph only."""
import numpy as np

def direction_details(seq,node,score):
    n=len(score)
    if not n:return {'position':np.empty(0,np.int64),'margin':np.empty(0),'competitor':np.empty(0),'exists':np.empty(0,bool),'rank':np.empty(0,np.int64),'group_best_tie_count':np.empty(0,np.int64),'competitor_tie_count':np.empty(0,np.int64)}
    order=np.lexsort((np.arange(n),-score,node,seq));s=seq[order];v=node[order];starts=np.flatnonzero(np.r_[True,(s[1:]!=s[:-1])|(v[1:]!=v[:-1])]);ends=np.r_[starts[1:],n];counts=ends-starts;first=np.repeat(order[starts],counts);second=np.repeat(order[starts+np.minimum(1,counts-1)],counts);rank=np.arange(n)-np.repeat(starts,counts);exists=np.repeat(counts>1,counts);alt=np.where(rank==0,second,first);alt[~exists]=-1;comp=np.full(n,np.nan);comp[exists]=score[alt[exists]];margin=score[order]-comp
    eqbest=score[order]==score[first];eqsecond=score[order]==score[second];bc=np.add.reduceat(eqbest.astype(np.int64),starts);sc=np.add.reduceat(eqsecond.astype(np.int64),starts);bt=np.repeat(bc,counts);ct=np.where(rank==0,np.repeat(sc,counts),bt)-(score[order]==comp).astype(np.int64);ct[~exists]=0
    out={}
    for key,value in [('position',alt),('margin',margin),('competitor',comp),('exists',exists),('rank',rank+1),('group_best_tie_count',bt),('competitor_tie_count',ct)]:
        x=np.empty_like(value);x[order]=value;out[key]=x
    return out

def extract_competition(graph,delta=.03):
    assert delta>0
    score=graph['score'];out={};a=[]
    for side,nodefield in [('source','source'),('destination','destination')]:
        d=direction_details(graph['sequence_index'],graph[nodefield],score)
        for k,v in d.items():out[side+'_'+k]=v
        valid=d['exists'];positions=d['position'];z=np.zeros(len(score));z[valid]=np.clip(1-np.maximum(d['margin'][valid],0)/delta,0,1);out[side+'_ambiguity']=z;a.append(z);ids=np.full(len(score),-1,np.int64);ids[valid]=graph['edge_id'][positions[valid]];out[side+'_competitor_edge_id']=ids
        other='destination' if side=='source' else 'source';ends=np.full(len(score),-1,np.int64);ends[valid]=graph[other][positions[valid]];out[side+'_competitor_endpoint']=ends
    out['ambiguity_b1']=np.maximum(*a);return out
