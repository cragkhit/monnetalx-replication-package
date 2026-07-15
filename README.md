# monnetalx-replication-package

Welcome to the replication package for our study on hyperlinks in Pull Request (PR) descriptions. 

This repository contains all the code, datasets, and analysis scripts necessary to replicate our methodology and answer our three primary Research Questions (RQs) regarding how developers use, rank, and perceive hyperlinks during the PR review process.

---

## 🎯 Research Questions

### RQ1: Link Prevalence and Distribution
**How prevalent are hyperlinks in PR descriptions, and what is their distribution across different types of resources?**
* **Context:** Understanding the landscape of hyperlink usage in PR descriptions is critical for motivating and designing an effective ranking approach. 
* **Approach:** This question is addressed through a large-scale analysis of PR descriptions across multiple repositories, characterizing link frequency, types (e.g., internal vs. external), and distribution patterns.

### RQ2: Effectiveness of Ranking Techniques
**What is the effectiveness of different techniques in ranking links in PR descriptions based on their relevance?**
* **Context:** Identifying the most effective approach for ordering links by contextual relevance is essential for reducing reviewer cognitive load.
* **Approach:** We evaluate the performance of several link ranking techniques on a manually annotated dataset of PR descriptions. The techniques evaluated include TF-IDF, LLM-based encoders, cross-encoder rerankers, and learning-to-rank (LTR) models.

### RQ3: Developer Perception
**How do software developers perceive the effectiveness of the link ranking approach during PR reviews?**
* **Context:** It is vital to understand the practical impact of our approach on the actual PR review process.
* **Approach:** We conducted a human evaluation with professional developers to assess perceived effectiveness in helping reviewers quickly understand linked resources.

---

## 🔗 Related Tools & Resources
* **AILinkPreviewer:** [https://github.com/c4rtune/AILinkPreviewer](https://github.com/c4rtune/AILinkPreviewer)

*(Note: For specific datasets and scripts related to each research question, please navigate to their respective folders within this repository.)*
