# Replication Package: Which Link Should I Look At First? Automated Link Ranking in Code Reviews

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23383155.svg)](https://doi.org/10.5281/zenodo.23383155)

This is the replication package for our paper, accepted at the **33rd Asia-Pacific Software Engineering Conference ([APSEC 2026](https://conf.researchr.org/home/apsec-2026))**, Bali, Indonesia, December 7–10, 2026:

> Panya Trakoolgerntong, Arus Thienmee, Patsathorn Chadbantern, Chaiyong Ragkhitwetsagul, Morakot Choetkiertikul, Tao Xiao, Patanamon Thongtanunam, and Yasutaka Kamei. **Which Link Should I Look At First?: Automated Link Ranking in Code Reviews.** In *Proceedings of the 33rd Asia-Pacific Software Engineering Conference (APSEC 2026)*, 2026.

It contains the code, datasets, and analysis scripts needed to replicate our methodology and answer our three Research Questions (RQs) about how developers use, rank, and perceive hyperlinks during PR review.

---

## 📂 Contents

| Folder | Content |
|---|---|
| [`RQ1/`](RQ1/) | Scripts for the large-scale analysis of links in PR descriptions, and the 700-PR stratified sample used in RQ2 |
| [`RQ2/`](RQ2/) | Annotated ground truth, notebooks and scripts for every ranking technique, the per-link rankings, and the evaluation with confidence intervals and significance tests (Table IV) |
| [`RQ3/`](RQ3/) | Human evaluation: methodology, links to the survey forms, and de-identified survey responses with a codebook |

Each folder has its own README with step-by-step instructions.

---

## 🎯 Research Questions

### RQ1: Link Prevalence and Distribution
**How prevalent are hyperlinks in PR descriptions, and what is their distribution across different types of resources?**
* **Context:** Understanding the landscape of hyperlink usage in PR descriptions is critical for motivating and designing an effective ranking approach.
* **Approach:** A large-scale analysis of PR descriptions from the 50 most-starred GitHub repositories, characterizing link frequency, types (e.g., internal vs. external), and distribution patterns.

### RQ2: Effectiveness of Ranking Techniques
**What is the effectiveness of different techniques in ranking links in PR descriptions based on their relevance?**
* **Context:** Identifying the most effective approach for ordering links by contextual relevance is essential for reducing reviewer cognitive load.
* **Approach:** We evaluate several link ranking techniques on a manually annotated dataset of PR descriptions: TF-IDF, a Sentence-BERT encoder, LLM-based encoders, a cross-encoder reranker, and learning-to-rank (LTR) models. We also compare them with the PR author's original link order.

### RQ3: Developer Perception
**How do software developers perceive the effectiveness of the link ranking approach during PR reviews?**
* **Context:** It is vital to understand the practical impact of our approach on the actual PR review process.
* **Approach:** A human evaluation with 14 developers, assessing how well the approach helps reviewers quickly understand linked resources.

---

## 🔗 Related Resources
* **Full RQ1 dataset (Hyperlinks in PR Descriptions):** [https://zenodo.org/records/21343748](https://zenodo.org/records/21343748)
* **Source repository of this package:** [https://github.com/cragkhit/monnetalx-replication-package](https://github.com/cragkhit/monnetalx-replication-package)
* **AILinkPreviewer:** [https://github.com/c4rtune/AILinkPreviewer](https://github.com/c4rtune/AILinkPreviewer)

---

## 📜 License
* **Code** (`.py` scripts and `.ipynb` notebooks): MIT License.
* **Data and documentation** (all other files): Creative Commons Attribution 4.0 International (CC BY 4.0).

The datasets include PR descriptions and text fetched from linked resources. That content remains subject to its original authors' licenses and terms. See [`LICENSE`](LICENSE) for details.

## 📝 How to Cite
If you use this package, please cite the paper above and this replication package:

> Panya Trakoolgerntong, Arus Thienmee, Patsathorn Chadbantern, Chaiyong Ragkhitwetsagul, Morakot Choetkiertikul, Tao Xiao, Patanamon Thongtanunam, and Yasutaka Kamei. *Replication Package for "Which Link Should I Look At First?: Automated Link Ranking in Code Reviews".* Zenodo, 2026. [https://doi.org/10.5281/zenodo.23383155](https://doi.org/10.5281/zenodo.23383155)

Citation metadata is also in [`CITATION.cff`](CITATION.cff).
