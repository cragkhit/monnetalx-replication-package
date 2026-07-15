# Research Question 2: Link Ranking Effectiveness

This folder contains the scripts, notebooks, and datasets relevant to **Research Question 2 (RQ2):** *What is the effectiveness of different techniques in ranking links in PR descriptions based on their relevance?*

## Overview
To address this question, we evaluate the performance of several link-ranking techniques to determine the most effective approach for ordering links by contextual relevance. This evaluation compares traditional baselines, Learning to Rank (LTR) models, and modern Large Language Models (LLMs) against a manually annotated ground-truth dataset.

---

## ⚙️ Prerequisites
To run the Jupyter Notebooks, ensure your environment is set up with the following:
* **Python 3.x**
* **Machine Learning Libraries:** `torch`, `transformers`, `sentence-transformers`, `lightgbm`, `xgboost`, `scikit-learn`
* **Data Handling:** `pandas`, `numpy`, `PyGithub`
* **GPU:** Highly recommended for running LLM evaluations and Cross-Encoder rerankers.

---

## 🚀 How to Run the Code

The evaluation pipeline is designed to be run in two distinct stages using the provided Jupyter Notebooks:

### Stage 1: Train the Learning-to-Rank (LTR) Model
Use `LTR (1).ipynb` to build and train your ranking models.
1. **Load Data:** The script loads the ground-truth `processed_700_sample.csv`.
2. **Feature Engineering:** It extracts contextual features (e.g., cosine similarity, n-gram overlaps, repository metadata).
3. **Training & Cross-Validation:** The notebook executes a 10-fold cross-validation process to train the LTR models (LightGBM/XGBoost).
4. **Output:** The script saves the best-performing model's predictions to a CSV file (e.g., `10foldx.csv`), which is required for final metric comparison.

### Stage 2: Comparative Evaluation
Use `evalMonnetalv2.ipynb` to compare your LTR model against other baselines.
1. **Load Models:** The script imports the ranking results from various techniques, including TF-IDF, Sentence Transformers, Cross-Encoders, and LLMs (e.g., Mistral-7B).
2. **Calculate Metrics:** It processes these rankings against the ground truth to calculate standardized metrics:
   * **NDCG@10** (Normalized Discounted Cumulative Gain)
   * **MRR** (Mean Reciprocal Rank)
   * **Precision@1**
   * **Kendall's Tau**
3. **Compilation:** The final comparison results are generated and stored in the evaluation results folder.

---

## 📂 Folder Contents

### 📓 Notebooks
* **`LTR (1).ipynb`** Handles feature engineering, training, and cross-validation of LTR models.
* **`evalMonnetalv2.ipynb`** Evaluates and compares baseline and SOTA ranking techniques.

### 📊 Datasets & Ground Truth
* **`processed_700_sample.csv`** The manually annotated ground-truth dataset (700 stratified samples).

### 📈 Evaluation Results
* **`lastEval-20260712T071853Z-2-001.zip`** Compiled CSV result files for the various tested models.
* **`chatgpt_prompt_full.zip`** Raw outputs and ranking results received from the ChatGPT baseline.
