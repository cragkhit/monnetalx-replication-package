import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load CSV
df = pd.read_csv("link_count.csv")

# Ensure numeric
df["link_count"] = pd.to_numeric(df["link_count"], errors="coerce")
df = df.dropna(subset=["link_count"])


# Exclude specific repos
exclude_repos = [""]
df = df[~df["repo"].isin(exclude_repos)]

# ======================================================
# Compute quartiles + print their values
# Quartiles
q1 = df["link_count"].quantile(0.25)
q2 = df["link_count"].quantile(0.50)  # median
q3 = df["link_count"].quantile(0.75)
q4 = df["link_count"].max()

print("Quartile values:")
print(f"Q1 (25%): {q1}")
print(f"Q2 (50% / median): {q2}")
print(f"Q3 (75%): {q3}")
print(f"Q4 (max): {q4}")


q3_q4_link_count_sum = df[df["link_count"] >= q3]["link_count"].sum()

print(f"Sum of link_count values in Q3–Q4 (>= Q3): {q3_q4_link_count_sum}")

# Rows in Q3–Q4 (>= Q3)
rows_q3_q4 = df[df["link_count"] >= q3].shape[0]

print(f"Number of rows in CSV within Q3–Q4 (>= Q3): {rows_q3_q4}")


# ======================================================

df_q3_q4 = df[df["link_count"] >= q3]

repo_counts = (
    df_q3_q4
    .groupby("repo")
    .size()
    .reset_index(name="q3_q4_occurrences")
    .sort_values(by="q3_q4_occurrences", ascending=False)
)

repo_avg_link_count = (
    df_q3_q4
    .groupby("repo")["link_count"]
    .mean()
    .reset_index(name="avg_link_count_q3_plus")
)

repo_summary = (
    repo_counts
    .merge(repo_avg_link_count, on="repo")
    .sort_values(by="q3_q4_occurrences", ascending=False)
)

print("\nRepos in Q3–Q4 (sorted by frequency):")
print(repo_summary)

# ======================================================

# TOTAL_SAMPLE_SIZE = 500  # adjust as needed

# repo_counts["sample_size"] = (
#     repo_counts["q3_q4_occurrences"]
#     / repo_counts["q3_q4_occurrences"].sum()
#     * TOTAL_SAMPLE_SIZE
# ).round().astype(int)

# stratified_sample = (
#     df_q3_q4
#     .merge(repo_counts[["repo", "sample_size"]], on="repo")
#     .groupby("repo", group_keys=False)
#     # .apply(lambda x: x.sample(n=min(len(x), x["sample_size"].iloc[0]), random_state=42))
#     .apply(lambda x: x.sample(n=min(len(x), x["sample_size"].iloc[0])))
#     .drop(columns="sample_size")
# )

# sample_repo_counts = (
#     stratified_sample
#     .groupby("repo")
#     .size()
#     .reset_index(name="sample_occurrences")
#     .sort_values(by="sample_occurrences", ascending=False)
# )

# print("\nSample repo distribution:")
# print(sample_repo_counts)

# stratified_sample.to_csv("repo_stratified_q3_q4_sample.csv", index=False)

# ======================================================

# # Print ~10 pr_link that fall in Q3 (50–75%)
# q4_prs = df[
#     (df["link_count"] > q3) &
#     (df["link_count"] <= q4)
# ][["pr_link", "link_count"]]


# q4_sample = q4_prs.sample(
#     n=min(30, len(q4_prs)),
#     random_state=42
# )

# print("\nSample PRs in Q4 (75–100% range):")
# print(q4_sample.to_string(index=False))


# q3_to_q4 = df.loc[
#     df["link_count"] >= q3,
#     "link_count"
# ]

# # Sort values descending
# sorted_q3_to_q4 = sorted(q3_to_q4.tolist(), reverse=True)

# # Print horizontally
# # print(", ".join(map(str, sorted_q3_to_q4)))

# with open("q3_to_q4_link_counts_desc.txt", "w") as f:
#     f.write(", ".join(map(str, sorted_q3_to_q4)))

# ======================================================
# Box plot showing the distribution
# plt.figure()
# plt.boxplot(df["link_count"], showfliers=True)
# plt.ylabel("link_count")
# plt.title("Box Plot of link_count (Q1–Q4)")
# plt.show()
