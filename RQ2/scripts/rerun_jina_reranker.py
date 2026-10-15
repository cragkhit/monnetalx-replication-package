"""Re-score the test PRs with jina-reranker-v3, fixing two bugs in
notebooks/2_rank_and_evaluate.ipynb (cell 13).

1. model.rerank() returns results sorted by relevance, each with the 'index' of the input document.
   The notebook wrote the scores back by sorted position, so the first link always got the highest
   score and the predicted order equalled the author's order.
2. The list of link documents was never reset, so every PR was reranked together with the documents
   of all earlier PRs (which also appended 352 empty rows to the output file).

Inputs are the PR bodies and fetched link documents stored in the original (buggy) output,
rankings/superseded/reranker_jina_v3_buggy.csv. They are the same texts used for the other models,
so nothing is re-scraped.

Usage:  python scripts/rerun_jina_reranker.py
Needs:  torch, transformers, pandas (downloads jinaai/jina-reranker-v3, which uses trust_remote_code)
Output: rankings/table_iv/reranker_jina_v3.csv (same columns as the input, empty rows dropped)
"""
from pathlib import Path

import pandas as pd
import torch
from transformers import AutoModel

RQ2 = Path(__file__).resolve().parent.parent
INPUT = RQ2 / "rankings" / "superseded" / "reranker_jina_v3_buggy.csv"
OUTPUT = RQ2 / "rankings" / "table_iv" / "reranker_jina_v3.csv"
MODEL_ID = "jinaai/jina-reranker-v3"
REVISION = "d7d7e73b6ea138ced340b83865931b5dfb6c97aa"  # revision used for the reported results

if torch.cuda.is_available():
    device, dtype = "cuda", "auto"
elif torch.backends.mps.is_available():
    device, dtype = "mps", torch.float32
else:
    device, dtype = "cpu", torch.float32

model = AutoModel.from_pretrained(MODEL_ID, revision=REVISION, dtype=dtype, trust_remote_code=True)
model = model.to(device).eval()
print(f"{MODEL_ID} (revision {REVISION}) on {device}")

ds = pd.read_csv(INPUT).dropna(subset=["uid"])
ds = ds.sort_values(["uid", "link_index"]).reset_index(drop=True)
ds["score"] = float("nan")

with torch.no_grad():
    for uid, g in ds.groupby("uid", sort=False):
        body = str(g["body"].iloc[0]) if pd.notna(g["body"].iloc[0]) else ""
        docs = [str(d) if pd.notna(d) else "" for d in g["doc"]]
        for r in model.rerank(body, docs):
            ds.loc[g.index[r["index"]], "score"] = r["relevance_score"]
        print(f"uid {int(uid)}: {len(docs)} links scored")

assert ds["score"].notna().all(), "some links were not scored"
ds["rerank"] = ds.groupby("uid")["score"].rank(method="first", ascending=False).astype(int)
ds["model_revision"] = REVISION

ds.to_csv(OUTPUT, index=False)
same = ds.groupby("uid").apply(lambda g: (g["rerank"].to_numpy() == g["link_index"].rank().to_numpy()).all(),
                               include_groups=False).sum()
print(f"Wrote {OUTPUT}  ({len(ds)} links, {ds['uid'].nunique()} PRs; "
      f"predicted order equals author order in {same} PRs)")
