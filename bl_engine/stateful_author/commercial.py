from dataclasses import dataclass
from .serial import relationship_productive

@dataclass(frozen=True)
class CommercialResult:
    failures:list[str]
    vector:dict[str,float]


def _max_consecutive_cliff_only(episodes):
    best=run=0
    for ep in episodes:
        d=ep['delta']
        if d.cliffhanger_only and not d.has_progress():
            run+=1; best=max(best,run)
        else: run=0
    return best


def evaluate_commercial_arc(episodes:list[dict],transformations:list)->CommercialResult:
    n=max(1,len(episodes))
    progress=[bool(ep['delta'].has_progress()) for ep in episodes]
    coverage=sum(progress)/n
    nontransformative={'CONSOLIDATE','INHABIT','RECOVER','CALIBRATE','INCUBATE','RELEASE'}
    progress_required=[ep for ep in episodes if getattr(ep['delta'],'metabolism',None) not in nontransformative]
    required_coverage=(sum(1 for ep in progress_required if ep['delta'].has_progress())/len(progress_required)) if progress_required else 1.0
    pressure_dims=set(); rel_events=0; linked_causal=0
    for ep in episodes:
        pressure_dims |= ep['pressure'].active_dimensions()
        rel_data=ep.get('relationship_data')
        if isinstance(rel_data,dict):
            if relationship_productive(rel_data): rel_events+=1
        elif ep['delta'].relationship_changes and ep.get('relationship_evidence'):
            rel_events+=1
        linked_causal += 1 if ep.get('causal_links') else 0
    valid=sum(1 for t in transformations if t.is_valid())
    failures=[]
    if _max_consecutive_cliff_only(episodes)>=3: failures.append('SERIAL_STAGNATION')
    if progress_required and required_coverage<0.5: failures.append('FALSE_PROGRESS')
    vector={
      'episode_delta_coverage':round(coverage,3),
      'pressure_diversity':round(min(1.0,len(pressure_dims)/8),3),
      'relationship_productivity':round(min(1.0,rel_events/n),3),
      'question_transformation':round(valid/max(1,len(transformations)),3) if transformations else 0.0,
      'causal_compounding':round(min(1.0,linked_causal/n),3),
    }
    return CommercialResult(failures,vector)
