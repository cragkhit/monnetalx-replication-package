import pandas as pd
import numpy as np
import os

# Files
INPUT_FILE = "output_q3_q4.csv"
LOG_FILE = "sampled_pr_links_log.csv"
OUTPUT_FILE = "stratified_sample.csv"

TOTAL_SAMPLES = 10

# Load dataset
df = pd.read_csv(INPUT_FILE)

# Load previously sampled pr_links if log exists
if os.path.exists(LOG_FILE):
    sampled_log = pd.read_csv(LOG_FILE)
    sampled_links = set(sampled_log["pr_link"])
    df = df[~df["pr_link"].isin(sampled_links)]  # exclude already sampled
    print(f"Excluded {len(sampled_links)} previously sampled PRs.")
else:
    sampled_links = set()

# Count occurrences per repo
repo_counts = df["repo"].value_counts()

# Compute proportional sample sizes
repo_proportions = repo_counts / repo_counts.sum()
repo_sample_sizes = (repo_proportions * TOTAL_SAMPLES).round().astype(int)

# Fix rounding issues
difference = TOTAL_SAMPLES - repo_sample_sizes.sum()
if difference != 0:
    for repo in repo_sample_sizes.index[:abs(difference)]:
        repo_sample_sizes[repo] += np.sign(difference)

# Stratified sampling
samples = []

for repo, n in repo_sample_sizes.items():
    repo_df = df[df["repo"] == repo]
    n = min(n, len(repo_df))
    if n > 0:
        samples.append(repo_df.sample(n=n, random_state=42))

sampled_df = pd.concat(samples).sample(frac=1, random_state=42)

# Save sampled output
sampled_df.to_csv(OUTPUT_FILE, index=False)

# Update log
new_links = sampled_df[["pr_link"]]

if os.path.exists(LOG_FILE):
    updated_log = pd.concat([sampled_log, new_links]).drop_duplicates()
else:
    updated_log = new_links

updated_log.to_csv(LOG_FILE, index=False)

print(f"Saved {len(sampled_df)} rows to {OUTPUT_FILE}")
print(f"Log updated with {len(new_links)} new pr_links.")