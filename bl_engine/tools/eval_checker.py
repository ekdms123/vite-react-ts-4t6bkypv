#!/usr/bin/env python3
"""BL VOICE ENGINE — eval_checker.py

검사기 자체를 시험한다. '사람 원작 덩어리를 얼마나 통과시키는가'와 'AI 덩어리를 얼마나 잡는가'.
판별기는 시험 대상 작품/파일을 뺀 나머지로 매번 다시 학습한다(leave-one-group-out). 학습한 글로 시험하지 않는다.

  python tools/eval_checker.py --human 원작폴더 --ai AI폴더 [--json 결과.json]
(numpy·scikit-learn 필요)
"""
from __future__ import annotations
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--human', required=True)
    ap.add_argument('--ai', required=True)
    ap.add_argument('--per-work', type=int, default=80)
    ap.add_argument('--json')
    a = ap.parse_args()
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    import voicecheck as vc
    import discriminator as dz
    from train_discriminator import load_human, load_ai
    from stylofeat import features

    hx, hg = load_human(a.human, a.per_work)
    ax, ag = load_ai(a.ai)
    texts, groups = hx + ax, hg + ag
    y = np.array([1] * len(hx) + [0] * len(ax))
    F = [features(t) for t in texts]
    names = sorted(k for k in F[0] if not k.startswith('_'))
    X = np.array([[f[k] for k in names] for f in F], dtype=float)
    rows = []
    for g in sorted(set(groups)):
        te = np.array([x == g for x in groups])
        mu = X[~te].mean(0); sd = X[~te].std(0) + 1e-6
        m = LogisticRegression(C=0.3, class_weight='balanced', max_iter=5000).fit((X[~te] - mu) / sd, y[~te])
        Xh = X[~te][y[~te] == 1]
        model = {'features': names, 'mean': list(mu), 'std': list(sd), 'coef': list(m.coef_[0]), 'intercept': float(m.intercept_[0]),
                 'human_means': list(Xh.mean(0)), 'human_p05': list(np.percentile(Xh, 5, 0)), 'human_p95': list(np.percentile(Xh, 95, 0)),
                 'eval': {'auc': None}}
        dz._M = model
        for i in np.where(te)[0]:
            f, iss, s, v = vc.score(texts[i])
            p = f['_disc']['p_human_min'] if f.get('_disc') else None
            rows.append({'group': g, 'human': bool(y[i]), 'pattern_score': s, 'p_human': p,
                         'v5_pass': v.startswith('PASS'), 'pattern_only_pass': s <= vc.TARGETS['pass_threshold']})
    dz._M = None
    out = {}
    for lab, hum in (('human', True), ('ai', False)):
        rs = [r for r in rows if r['human'] == hum]
        out[lab] = {'n': len(rs), 'v5_pass_rate': round(sum(r['v5_pass'] for r in rs) / len(rs), 3),
                    'pattern_only_pass_rate': round(sum(r['pattern_only_pass'] for r in rs) / len(rs), 3)}
    out['by_group'] = {}
    for g in sorted(set(groups)):
        rs = [r for r in rows if r['group'] == g]
        out['by_group'][g] = {'n': len(rs), 'v5_pass_rate': round(sum(r['v5_pass'] for r in rs) / len(rs), 3),
                              'p_human_mean': round(float(np.mean([r['p_human'] for r in rs])), 3)}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    if a.json:
        json.dump({'summary': out, 'rows': rows}, open(a.json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
