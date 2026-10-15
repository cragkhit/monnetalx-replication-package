"""RQ2 link-ranking evaluation with confidence intervals and paired significance tests.

Recomputes Table IV from the per-link ranking files in rankings/table_iv/ and compares the best
model (LightGBM-8) against every other approach, PR by PR. The Original baseline (the PR author's
link order) is derived from link_index.

Metrics (per PR, then averaged over PRs):
  NDCG@10  graded relevance n - rank + 1 (ground-truth rank 1 = most relevant), links ordered by predicted rank
  P@1      1 if the model's top-ranked link is the ground-truth rank-1 link, else 0
  MRR      1 / predicted position of the ground-truth rank-1 link
  KT       Kendall's tau-b between ground-truth and predicted ranks

Ties: models often give several links the same score (e.g., LightGBM, or links whose content could not be
fetched). --ties author (default, as reported in the paper) breaks ties by the order of the links in the PR
description. --ties random instead averages each per-PR metric over random tie orders, as a sensitivity check
of how much the models rely on the author's order.

Statistics:
  95% CIs  percentile bootstrap over PRs (shared resamples across models, so differences are paired)
  Tests    two-sided paired randomization (sign-flip) test for NDCG@10, MRR and KT;
           exact McNemar test for P@1 when both models' per-PR P@1 values are 0/1
           (randomization test otherwise, since averaging over random tie orders makes P@1 fractional)
  Holm     across the comparisons against LightGBM-8 within each metric
           (p_holm_all: across all comparisons and metrics, as a stricter check)

Usage:  python scripts/evaluate_rankings.py [--ties author|random] [rankings_dir] [out_dir]
        (defaults: rankings/table_iv/ and evaluation/, relative to the RQ2 folder)
Needs:  numpy, pandas, scipy
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest, kendalltau, rankdata

RQ2 = Path(__file__).resolve().parent.parent
ARGS = sys.argv[1:]
TIES = "author"
if "--ties" in ARGS:
    i = ARGS.index("--ties")
    TIES = ARGS[i + 1]
    del ARGS[i:i + 2]
assert TIES in ("random", "author"), "--ties must be 'random' or 'author'"
RANKINGS = Path(ARGS[0]) if len(ARGS) > 0 else RQ2 / "rankings" / "table_iv"
OUT = (Path(ARGS[1]) if len(ARGS) > 1 else RQ2 / "evaluation") / f"ties_{TIES}"

BEST = "LightGBM-8"
SEED = 42
N_BOOT = 10_000
N_PERM = 100_000
N_TIE_DRAWS = 1_000
ALPHA = 0.05
METRICS = ["ndcg10", "p1", "mrr", "kt"]
METRIC_NAMES = {"ndcg10": "NDCG@10", "p1": "P@1", "mrr": "MRR", "kt": "KT"}

# Table IV rows: (display name, group, ranking file). Original is derived from link_index.
MODELS = [
    ("Original", None, None),
    ("TF-IDF", None, "tfidf.csv"),
    ("all_minilm_l6_v2", "SBERT Encoder", "sbert_all_minilm_l6_v2.csv"),
    ("jina_reranker", "Reranker (Cross-Encoder)", "reranker_jina_v3.csv"),
    ("deepseek_coder", "LLM as Encoders", "llm_deepseek_coder.csv"),
    ("mistral7B", "LLM as Encoders", "llm_mistral_7b.csv"),
    ("LightGBM-4-features", "Learning-to-rank (LTR)", "ltr_lightgbm_4f.csv"),
    (BEST, "Learning-to-rank (LTR)", "ltr_lightgbm_8f.csv"),
]
LABEL = {BEST: "LightGBM-8-features"}


# ---------------------------------------------------------------- per-PR metrics
def ndcg_at_k(gt_rank, pred_rank, k=10):
    n = len(gt_rank)
    rel = n - gt_rank + 1
    disc = 1 / np.log2(np.arange(2, n + 2))[:k]
    dcg = (rel[np.argsort(pred_rank, kind="stable")][:k] * disc).sum()
    idcg = (np.sort(rel)[::-1][:k] * disc).sum()
    return dcg / idcg


def metrics_for_order(gt, order):
    """gt: ground-truth positions 1..n; order: link indices from first to last as shown by the model."""
    pred = np.empty(len(gt))
    pred[order] = np.arange(1, len(gt) + 1)
    return (ndcg_at_k(gt, pred), float(gt[order[0]] == 1), 1 / pred[gt == 1][0], kendalltau(gt, pred).statistic)


def per_pr_scores(df, rng):
    """df needs uid, link_index, rank and a numeric 'score' (higher = more relevant)."""
    rows = []
    for uid, g in df.sort_values(["uid", "link_index"]).groupby("uid"):
        gt = rankdata(g["rank"].to_numpy(), method="ordinal").astype(float)  # positions 1..n
        score = g["score"].to_numpy(float)
        if TIES == "author" or len(np.unique(score)) == len(score):
            vals = [metrics_for_order(gt, np.lexsort((np.arange(len(score)), -score)))]
        else:
            vals = [metrics_for_order(gt, np.lexsort((rng.random(len(score)), -score))) for _ in range(N_TIE_DRAWS)]
        m = np.mean(vals, axis=0)
        rows.append(dict(uid=int(uid), n_links=len(g), tied_links=int(pd.Series(score).duplicated(keep=False).sum()),
                         ndcg10=m[0], p1=m[1], mrr=m[2], kt=m[3]))
    return pd.DataFrame(rows)


def parse_score(x):
    """Scores are floats, or strings such as 'tensor([0.4090])'."""
    m = re.search(r"-?\d+(?:\.\d*)?(?:[eE]-?\d+)?", str(x))
    return float(m.group()) if m else np.nan


def load(fname):
    df = pd.read_csv(RANKINGS / fname, usecols=["uid", "link_index", "rank", "score"]).dropna(subset=["uid"])
    df["score"] = df["score"].map(parse_score)
    assert df["score"].notna().all(), f"{fname}: unparseable scores"
    return df.astype({"uid": int, "link_index": int, "rank": int})


# ---------------------------------------------------------------- statistics
def perm_test(d, rng):
    """Two-sided paired randomization test on the mean difference (Monte Carlo sign flips)."""
    obs = abs(d.mean())
    hits = 0
    for start in range(0, N_PERM, 10_000):
        signs = rng.choice([-1.0, 1.0], size=(min(10_000, N_PERM - start), len(d)))
        hits += (np.abs((signs * d).mean(axis=1)) >= obs - 1e-12).sum()
    return (hits + 1) / (N_PERM + 1)


def rank_biserial(d):
    """Matched-pairs rank-biserial correlation (zero differences dropped)."""
    d = d[d != 0]
    if len(d) == 0:
        return 0.0
    r = rankdata(np.abs(d))
    return (r[d > 0].sum() - r[d < 0].sum()) / r.sum()


def holm(p):
    p = np.asarray(p, float)
    order = np.argsort(p)
    adj = np.empty_like(p)
    running = 0.0
    for i, idx in enumerate(order):
        running = max(running, (len(p) - i) * p[idx])
        adj[idx] = min(1.0, running)
    return adj


def ci(boot_means):
    return np.percentile(boot_means, [2.5, 97.5])


# ---------------------------------------------------------------- main
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    scores = {}
    for name, _, fname in MODELS:
        if fname is None:  # author's order: earlier links score higher (link_index has gaps in some PRs)
            scores[name] = per_pr_scores(load("ltr_lightgbm_8f.csv").assign(score=lambda d: -d["link_index"]), rng)
        else:
            scores[name] = per_pr_scores(load(fname), rng)

    uids = scores[BEST]["uid"].to_numpy()
    for name, s in scores.items():
        assert np.array_equal(s["uid"].to_numpy(), uids), f"{name}: PR set differs from {BEST}"
    n = len(uids)

    long = pd.concat([s.assign(model=m) for m, s in scores.items()], ignore_index=True)
    long.to_csv(OUT / "per_pr_scores.csv", index=False)

    # expected score of a random ordering, for reference
    ref = load("ltr_lightgbm_8f.csv")
    rand = []
    for _ in range(200):
        shuffled = ref.assign(score=ref.groupby("uid")["rank"].transform(lambda s: rng.permutation(len(s))))
        rand.append(per_pr_scores(shuffled, rng)[METRICS].mean())
    rand = pd.concat(rand, axis=1).mean(axis=1)

    boot_idx = rng.integers(0, n, size=(N_BOOT, n))  # shared across models -> paired CIs

    # per-model means and CIs
    summary = []
    for name in scores:
        row = dict(model=name)
        for m in METRICS:
            x = scores[name][m].to_numpy()
            lo, hi = ci(x[boot_idx].mean(axis=1))
            row.update({m: x.mean(), f"{m}_lo": lo, f"{m}_hi": hi})
        summary.append(row)
    summary = pd.DataFrame(summary)
    summary.to_csv(OUT / "table_iv_summary.csv", index=False)

    # paired comparisons against BEST
    tests = []
    best = scores[BEST]
    for m in METRICS:
        b = best[m].to_numpy()
        for name in scores:
            if name == BEST:
                continue
            o = scores[name][m].to_numpy()
            d = b - o
            lo, hi = ci(d[boot_idx].mean(axis=1))
            row = dict(metric=METRIC_NAMES[m], vs=name, best=b.mean(), other=o.mean(), diff=d.mean(),
                       diff_lo=lo, diff_hi=hi)
            if m == "p1" and np.isin(np.r_[b, o], [0, 1]).all():  # tie averaging makes P@1 fractional
                wins = int(((b == 1) & (o == 0)).sum())    # best right, other wrong
                losses = int(((b == 0) & (o == 1)).sum())  # best wrong, other right
                row.update(test="McNemar (exact)", discordant=f"{wins}/{losses}",
                           effect=(wins - losses) / max(wins + losses, 1),
                           p_raw=binomtest(wins, wins + losses, 0.5).pvalue if wins + losses else 1.0)
            else:
                row.update(test="Randomization", discordant="", effect=rank_biserial(d), p_raw=perm_test(d, rng))
            tests.append(row)
    tests = pd.DataFrame(tests)
    tests["p_holm"] = tests.groupby("metric")["p_raw"].transform(holm)
    tests["p_holm_all"] = holm(tests["p_raw"])
    tests["significant"] = tests["p_holm"] < ALPHA
    tests.to_csv(OUT / "pairwise_tests.csv", index=False)

    # ------------------------------------------------------------ report
    pd.set_option("display.width", 200)
    print(f"Ties broken by: {TIES}   PRs: {n}   links: {int(scores[BEST]['n_links'].sum())}   "
          f"bootstrap: {N_BOOT}   permutations: {N_PERM}")
    print("Tied links per model: " + ", ".join(f"{m} {int(s['tied_links'].sum())}" for m, s in scores.items()) + "\n")
    print("Mean [95% CI]")
    for _, r in summary.iterrows():
        print(f"  {r.model:22s}" + "".join(
            f"  {METRIC_NAMES[m]} {r[m]:.3f} [{r[m + '_lo']:.3f}, {r[m + '_hi']:.3f}]" for m in METRICS))
    print("  " + "Random ordering (expected)".ljust(22) + "".join(f"  {METRIC_NAMES[m]} {rand[m]:.3f}" + " " * 16 for m in METRICS))
    print(f"\n{BEST} vs. each approach (effect: rank-biserial r; for P@1, (wins-losses)/discordant)")
    cols = ["metric", "vs", "diff", "diff_lo", "diff_hi", "test", "discordant", "effect", "p_raw", "p_holm", "p_holm_all", "significant"]
    print(tests[cols].round(4).to_string(index=False))

    tex = latex_table(summary, tests, n)
    (OUT / "table_iv.tex").write_text(tex)
    print(f"\nWrote {OUT}/per_pr_scores.csv, table_iv_summary.csv, pairwise_tests.csv, table_iv.tex")


def latex_table(summary, tests, n):
    sig = {(r.vs, r.metric) for r in tests.itertuples() if r.significant}
    best_val = {m: summary[m].max() for m in METRICS}
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Comparison of Link Ranking Models on the " + str(n) + r" Test PRs: Mean [95\% Bootstrap CI] "
        r"(P@1=Precision@1 and KT=Kendall's Tau). $^\dagger$: Significantly Lower than LightGBM-8-features "
        r"(Paired Test, Holm-Corrected $p<0.05$)}",
        r"\label{tab:autoeval}",
        r"\small",
        r"\begin{tabular}{lcccc}",
        r"\toprule",
        r"\textbf{Model} & \textbf{NDCG@10} & \textbf{P@1} & \textbf{MRR} & \textbf{KT} \\",
    ]
    group = "start"
    for r in summary.itertuples():
        g = next(gr for nm, gr, _ in MODELS if nm == r.model)
        if g != group or g is None:
            lines.append(r"\midrule")
            if g is not None:
                lines.append(r"\multicolumn{5}{l}{\textbf{" + g + r"}} \\")
            group = g
        label = LABEL.get(r.model, r.model).replace("_", r"\_")
        if g is None:
            label = r"\textbf{" + label + "}"
        cells = []
        for m in METRICS:
            v = getattr(r, m)
            s = f"{v:.3f}"
            if np.isclose(v, best_val[m]):
                s = r"\textbf{" + s + "}"
            if (r.model, METRIC_NAMES[m]) in sig:
                s += r"$^\dagger$"
            lo, hi = getattr(r, f"{m}_lo"), getattr(r, f"{m}_hi")
            cells.append(s + r" {\footnotesize[" + f"{lo:.2f}, {hi:.2f}" + "]}")
        lines.append(f"{label} & " + " & ".join(cells) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table*}", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
