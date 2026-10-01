from __future__ import annotations
from statistics import mean, median, pvariance


def _percentile(values:list[float], q:float)->float:
    if not values: return 0.0
    xs=sorted(values)
    if len(xs)==1: return xs[0]
    pos=(len(xs)-1)*q; lo=int(pos); hi=min(len(xs)-1,lo+1); frac=pos-lo
    return xs[lo]*(1-frac)+xs[hi]*frac


def stable_frontier_summary(samples:list[dict])->dict:
    keys=sorted({k for s in samples for k,v in s.items() if isinstance(v,(int,float)) and not isinstance(v,bool)})
    metrics={}
    for key in keys:
        vals=[float(s[key]) for s in samples if isinstance(s.get(key),(int,float)) and not isinstance(s.get(key),bool)]
        metrics[key]={
            'mean':round(mean(vals),6),'median':round(median(vals),6),'p10':round(_percentile(vals,.10),6),
            'p05':round(_percentile(vals,.05),6),'variance':round(pvariance(vals),6) if len(vals)>1 else 0.0,'n':len(vals),
        }
    return {'metrics':metrics,'sample_count':len(samples),'aggregation':'PARETO_DISTRIBUTION_ONLY'}
