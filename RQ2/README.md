# Research Question 2: Link Ranking Effectiveness

This folder contains the data, notebooks, scripts, and results for **Research Question 2 (RQ2):** *What is the effectiveness of different techniques in ranking links in PR descriptions based on their relevance?*

## Overview
We compare several link-ranking techniques against a manually annotated ground truth of 700 PRs: TF-IDF, a Sentence-BERT encoder, LLMs used as encoders, a cross-encoder reranker, and Learning-to-Rank (LTR) models. We also compare them with the PR author's own link order (the *Original* baseline). The LTR models are trained on 90% of the PRs. Every technique is evaluated on the same held-out test PRs (68 PRs, 356 links). We report NDCG@10, Precision@1, MRR, and Kendall's Tau, with 95% bootstrap confidence intervals and paired significance tests.

---

## 📂 Folder Structure

```
RQ2/
├── README.md
├── requirements.txt                    Python packages for the scripts/ folder
├── data/
│   ├── ground_truth_700_prs.csv        Manually annotated ground truth (700 PRs, one row per link)
│   └── chatgpt_raw_rankings.zip        Raw ranked link lists returned by ChatGPT (one .txt per PR)
├── notebooks/
│   ├── 1_train_ltr.ipynb               Step 1: feature extraction, 10-fold CV, LTR training
│   └── 2_rank_and_evaluate.ipynb       Step 2: rank links with TF-IDF, SBERT, LLM encoders, reranker, ChatGPT
├── scripts/
│   ├── rerun_jina_reranker.py          Step 3: re-score the test PRs with jina-reranker-v3 (bug fix)
│   └── evaluate_rankings.py            Step 4: metrics, 95% CIs, significance tests, LaTeX table
├── rankings/                           Per-link rankings produced by each technique on the test PRs
│   ├── table_iv/                       The techniques reported in Table IV of the paper
│   ├── other/                          Further configurations evaluated but not reported in Table IV
│   └── superseded/                     Outputs replaced by a corrected rerun (kept for transparency)
└── evaluation/                         Output of Step 4
    ├── ties_author/                    Ties in model scores broken by the author's link order (reported)
    └── ties_random/                    Ties broken at random (sensitivity analysis)
```

### Ranking files (`rankings/`)

| File | Technique |
|---|---|
| `table_iv/tfidf.csv` | TF-IDF |
| `table_iv/sbert_all_minilm_l6_v2.csv` | Sentence-BERT encoder (`all-MiniLM-L6-v2`) |
| `table_iv/llm_deepseek_coder.csv` | LLM as encoder (`deepseek-coder-1.3b-base`) |
| `table_iv/llm_mistral_7b.csv` | LLM as encoder (`Mistral-7B-v0.1`) |
| `table_iv/reranker_jina_v3.csv` | Cross-encoder reranker (`jina-reranker-v3`), produced by Step 3 |
| `table_iv/ltr_lightgbm_4f.csv` | LTR, LightGBM LambdaMART, 4 features |
| `table_iv/ltr_lightgbm_8f.csv` | LTR, LightGBM LambdaMART, 8 features (best model) |
| `other/ltr_lightgbm_19f.csv` | LTR, LightGBM, 19 features |
| `other/ltr_xgboost_{4f,8f,19f}.csv` | LTR, XGBoost, 4/8/19 features |
| `other/ltr_lightgbm_10fold_cv.csv` | LTR predictions written by the 10-fold cross-validation run in notebook 1 |
| `other/llm_chatgpt.csv` | ChatGPT ranking the links directly from a prompt |
| `superseded/reranker_jina_v3_buggy.csv` | Original jina-reranker-v3 output, affected by the bug fixed in Step 3. Do not use it for results. |

Each file has **one row per (PR, link)**. The key columns are:

| Column | Meaning |
|---|---|
| `uid` | PR identifier (matches `data/ground_truth_700_prs.csv`) |
| `pr_link`, `repo`, `pr_title` | The PR |
| `link_index` | Position of the link in the PR description (0 = first). It defines the *Original* baseline. It can have gaps where links were filtered out. |
| `link` | The linked URL |
| `rank` | **Ground-truth** rank from the manual annotation (1 = most relevant) |
| `score` | The technique's relevance score (higher = more relevant) |
| `rerank` | The technique's predicted rank (1 = ranked first) |
| `body`, `doc` | PR description and fetched content of the linked resource (in the non-LTR files) |

---

## ⚙️ Prerequisites

* **Notebooks (Steps 1–2):** Python 3, `torch`, `transformers`, `sentence-transformers`, `lightgbm`, `xgboost`, `scikit-learn`, `pandas`, `numpy`, `PyGithub`. A GPU is highly recommended for the LLM encoders and the reranker. The notebooks were run on Google Colab (see the path note below).
* **Scripts (Steps 3–4):** `pip install -r requirements.txt`. Step 4 needs only `numpy`, `pandas`, and `scipy`. Step 3 also needs `torch` and `transformers`, and runs on CUDA, Apple MPS, or CPU.

---

## 🚀 How to Run

**To reproduce Table IV from the provided rankings, only Step 4 is needed.** Steps 1–3 regenerate the rankings from scratch. Run all commands from this `RQ2/` folder.

### Step 1: Train the LTR models (`notebooks/1_train_ltr.ipynb`)
1. **Load data:** the manually annotated ground truth (`data/ground_truth_700_prs.csv`).
2. **Feature engineering:**
   * 4-feature set: SBERT cosine similarity between the PR description and the link content, a same-repository flag, a created-by-the-assigned-reviewer flag, and a code-change (diff) flag.
   * 8-feature set: adds query length and unigram/bigram/trigram overlap.
3. **Training and tuning:** 90/10 train/test split by PR, then grouped 10-fold cross-validation on the training PRs to select LightGBM/XGBoost hyperparameters (criterion: 0.5 × NDCG@10 + 0.5 × MRR).
4. **Output:** predictions on the test PRs, i.e. the `ltr_*.csv` files in `rankings/`.

### Step 2: Rank links with the other techniques (`notebooks/2_rank_and_evaluate.ipynb`)
1. **Fetch content:** the PR description (`body`) and the content of each linked resource (`doc`).
2. **Score each link** against the PR description with TF-IDF, SBERT, the LLM encoders (cosine similarity of embeddings), and jina-reranker-v3. ChatGPT's raw responses are in `data/chatgpt_raw_rankings.zip`. The notebook converts the parsed ChatGPT rankings (`eval/chatGPT.csv` on Drive) into the ranking format.
3. **Output:** the non-LTR files in `rankings/`.

> **Note:** The metric cell at the end of this notebook is superseded by Step 4. It passed ranks where scikit-learn's `ndcg_score` expects relevance scores, and it computed exact-position accuracy with `torchmetrics` instead of Precision@1. Use `scripts/evaluate_rankings.py` for all reported numbers.

### Step 3: Re-score with the cross-encoder reranker (`scripts/rerun_jina_reranker.py`)
```bash
python scripts/rerun_jina_reranker.py
```
The jina-reranker-v3 cell in notebook 2 had two bugs:
* **Wrong score assignment.** `model.rerank()` returns results sorted by score, each with the `index` of its input document. The cell wrote the scores back in sorted order, so the predicted order always equalled the author's order.
* **Documents carried over between PRs.** The list of documents was never reset, so each PR was reranked together with the documents of all earlier PRs.

The script fixes both bugs and reuses the PR descriptions and link contents stored in `rankings/superseded/reranker_jina_v3_buggy.csv`, so nothing is re-fetched. These are the same texts the other techniques used. The model revision is pinned (`d7d7e73b6ea138ced340b83865931b5dfb6c97aa`) and stored in the output's `model_revision` column. The output is deterministic. It writes `rankings/table_iv/reranker_jina_v3.csv` and takes a few minutes on a GPU or Apple-silicon Mac.

> The model is loaded with `trust_remote_code=True`, which runs jina's model code from Hugging Face.

### Step 4: Evaluate and test for significance (`scripts/evaluate_rankings.py`)
```bash
python scripts/evaluate_rankings.py                 # results reported in the paper (ties broken by author order)
python scripts/evaluate_rankings.py --ties random   # sensitivity analysis
```
For every technique in `rankings/table_iv/` and the *Original* baseline (derived from `link_index`), the script computes per-PR metrics:

| Metric | Definition |
|---|---|
| NDCG@10 | Graded relevance `n − rank + 1` (n = number of links in the PR); links in predicted order |
| P@1 | 1 if the top-ranked link is the ground-truth rank-1 link, else 0 |
| MRR | 1 / predicted position of the ground-truth rank-1 link |
| KT | Kendall's tau-b between ground-truth and predicted ranks |

It then compares the best model (LightGBM-8) with every other technique, PR by PR:
* **95% confidence intervals:** percentile bootstrap over PRs, 10,000 resamples, shared across techniques so that differences stay paired.
* **Significance tests:** two-sided paired randomization test (100,000 sign flips) for NDCG@10, MRR, and KT. For P@1, an exact McNemar test (or the randomization test when P@1 is fractional, see below).
* **Effect sizes:** matched-pairs rank-biserial correlation, and wins/losses on discordant PRs for P@1.
* **Multiple comparisons:** Holm correction across the 7 comparisons within each metric (`p_holm`). `p_holm_all` corrects across all 28 tests, as a stricter check.
* **Reference:** the expected score of a random ordering is printed for context.

**Ties.** Several techniques give some links exactly the same score (for example, when the content of a link could not be fetched; LightGBM in particular often does). With `--ties author` (default), tied links keep the order in which they appear in the PR description. With `--ties random`, each per-PR metric is averaged over 1,000 random tie orders. This makes P@1 fractional, so P@1 is then tested with the randomization test. Comparing the two modes shows how much each technique relies on the author's order to break ties.

Outputs in `evaluation/ties_<mode>/`:

| File | Content |
|---|---|
| `table_iv.tex` | Table IV in LaTeX: mean [95% CI], best values in bold, † = significantly lower than LightGBM-8 (Holm-corrected p < 0.05) |
| `table_iv_summary.csv` | Mean and 95% CI per technique and metric |
| `pairwise_tests.csv` | Each LightGBM-8 comparison: difference, 95% CI, test, effect size, raw and Holm-adjusted p-values |
| `per_pr_scores.csv` | Per-PR metric values for every technique (input to the tests) |

---

## 🗂️ Mapping to Notebook Paths

The notebooks were run on Google Colab and read and write files under `drive/MyDrive/monnetal/`. When re-running them, point those paths to this folder:

| Notebook path | File in this package |
|---|---|
| `lastEval/tf_idfv2.csv` | `rankings/table_iv/tfidf.csv` |
| `lastEval/all_minilm_l6_v2.csv` | `rankings/table_iv/sbert_all_minilm_l6_v2.csv` |
| `lastEval/deepseek_coder.csv` | `rankings/table_iv/llm_deepseek_coder.csv` |
| `lastEval/Mistral7B.csv` | `rankings/table_iv/llm_mistral_7b.csv` |
| `lastEval/jina_reranker.csv`, `fold8/jina_reranker.csv` | `rankings/superseded/reranker_jina_v3_buggy.csv` (corrected: `rankings/table_iv/reranker_jina_v3.csv`) |
| `lastEval/LGBM4f.csv`, `LGBM8f.csv`, `LGBM19f.csv` | `rankings/table_iv/ltr_lightgbm_4f.csv`, `rankings/table_iv/ltr_lightgbm_8f.csv`, `rankings/other/ltr_lightgbm_19f.csv` |
| `lastEval/xgb4f.csv`, `xgb8f.csv`, `xgb19f.csv` | `rankings/other/ltr_xgboost_{4f,8f,19f}.csv` |
| `lastEval/10foldx.csv` | `rankings/other/ltr_lightgbm_10fold_cv.csv` |
| `lastEval/ChatGPT.csv` | `rankings/other/llm_chatgpt.csv` |
| `processed_700_sample.csv` | `data/ground_truth_700_prs.csv` |
| `chatgpt_prompt_full/` | `data/chatgpt_raw_rankings.zip` |
