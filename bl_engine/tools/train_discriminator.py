#!/usr/bin/env python3
"""BL VOICE ENGINE — train_discriminator.py

사람 BL 원작 덩어리 vs AI 덩어리로 추상 문체 판별기를 학습하고 voice/discriminator_model.json을 쓴다.
(numpy·scikit-learn 필요. 배포된 판별기 실행은 표준 라이브러리만으로 된다.)

  python tools/train_discriminator.py --human 원작폴더 --ai AI폴더 [--per-work 80] [--out voice/discriminator_model.json]

- --human: 사람 원작 .txt 폴더(BL 원작만. 비BL·빙의글은 넣지 않는다 — 문체 기준이 흐려진다)
- --ai: AI 글 .txt/.md 폴더. 파일 안에서 ===== 줄로 장면을 나눌 수 있다.
- 평가: 작품/파일 하나를 통째로 빼고 학습해 그 묶음을 맞히는 방식(leave-one-group-out). 같은 작품의 다른 구간으로 시험하지 않는다.
- 모델 파일에는 특징 이름·평균·표준편차·가중치만 저장한다. 원작 텍스트는 들어가지 않는다.
"""
from __future__ import annotations
import argparse, glob, json, os, re, sys, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from stylofeat import features, chunk, normalize  # noqa: E402


def read(p):
    b = open(p, 'rb').read()
    for enc in ('utf-8', 'cp949', 'utf-16'):
        try:
            return b.decode(enc)
        except UnicodeDecodeError:
            pass
    return b.decode('utf-8', 'ignore')


def load_human(folder, per_work):
    X, groups = [], []
    for p in sorted(glob.glob(os.path.join(folder, '*.txt'))):
        cs = chunk(read(p))
        cs = cs[2:-2] if len(cs) > 10 else cs  # 머리말·후기 제외
        step = max(1, len(cs) // per_work)
        for c in cs[::step][:per_work]:
            X.append(c); groups.append('H:' + os.path.basename(p))
    return X, groups


def load_ai(folder):
    X, groups = [], []
    for p in sorted(glob.glob(os.path.join(folder, '*.txt')) + glob.glob(os.path.join(folder, '*.md'))):
        t = re.sub(r'<!--.*?-->', '', read(p), flags=re.S)
        scenes = [s for s in re.split(r'\n=+\n', t) if len(s.strip()) > 600]
        for s in scenes:
            cs = chunk(s, lo=1600) if len(s) > 3200 else [normalize(s)]
            for c in cs:
                X.append(c); groups.append('A:' + os.path.basename(p))
    return X, groups


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--human', required=True)
    ap.add_argument('--ai', required=True)
    ap.add_argument('--per-work', type=int, default=80)
    ap.add_argument('--out', default=os.path.join(os.path.dirname(HERE), 'voice', 'discriminator_model.json'))
    ap.add_argument('--C', type=float, default=0.3)
    a = ap.parse_args()
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score

    hx, hg = load_human(a.human, a.per_work)
    ax, ag = load_ai(a.ai)
    texts = hx + ax
    groups = hg + ag
    y = np.array([1] * len(hx) + [0] * len(ax))  # 1 = 사람
    F = [features(t) for t in texts]
    names = sorted(k for k in F[0] if not k.startswith('_'))
    X = np.array([[f[k] for k in names] for f in F], dtype=float)
    print(f'human chunks {len(hx)} from {len(set(hg))} works / ai chunks {len(ax)} from {len(set(ag))} files / features {len(names)}')

    def fit(Xtr, ytr):
        mu = Xtr.mean(0); sd = Xtr.std(0) + 1e-6
        m = LogisticRegression(C=a.C, class_weight='balanced', max_iter=5000)
        m.fit((Xtr - mu) / sd, ytr)
        return mu, sd, m

    # leave-one-group-out
    oof = np.zeros(len(y))
    for g in sorted(set(groups)):
        te = np.array([x == g for x in groups])
        mu, sd, m = fit(X[~te], y[~te])
        oof[te] = m.predict_proba((X[te] - mu) / sd)[:, 1]
    auc = roc_auc_score(y, oof)
    per_group = {}
    for g in sorted(set(groups)):
        idx = [i for i, x in enumerate(groups) if x == g]
        per_group[g] = round(float(np.mean(oof[idx])), 3)
    print('LOGO AUC', round(auc, 4))
    for g, v in per_group.items():
        print(f'  {g:40s} mean P(human) {v}')

    mu, sd, m = fit(X, y)
    coef = m.coef_[0]
    order = np.argsort(-np.abs(coef))
    print('top features (+ = 사람 쪽, - = AI 쪽)')
    for i in order[:25]:
        print(f'  {names[i]:24s} {coef[i]:+.3f}  human_mean {X[y==1,i].mean():.3f}  ai_mean {X[y==0,i].mean():.3f}')
    model = {
        'schema': 'bl_discriminator.v1',
        'features': names,
        'mean': [round(float(v), 6) for v in mu],
        'std': [round(float(v), 6) for v in sd],
        'coef': [round(float(v), 6) for v in coef],
        'intercept': round(float(m.intercept_[0]), 6),
        'human_means': [round(float(X[y == 1, i].mean()), 5) for i in range(len(names))],
        'human_p05': [round(float(np.percentile(X[y == 1, i], 5)), 5) for i in range(len(names))],
        'human_p95': [round(float(np.percentile(X[y == 1, i], 95)), 5) for i in range(len(names))],
        'eval': {'method': 'leave-one-group-out', 'auc': round(float(auc), 4), 'per_group_mean_p_human': per_group,
                 'n_human': int(len(hx)), 'n_ai': int(len(ax)), 'C': a.C},
        'training_set_fingerprint': hashlib.sha256('\n'.join(sorted(set(groups))).encode()).hexdigest()[:16],
        'note': '모델에는 특징 통계와 가중치만 있다. 원작 문장은 저장하지 않는다.',
    }
    json.dump(model, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('wrote', a.out)


if __name__ == '__main__':
    main()
