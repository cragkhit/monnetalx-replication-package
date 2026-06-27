import pandas as pd

# Load CSV
df = pd.read_csv("link_count.csv")

# Ensure numeric
df["link_count"] = pd.to_numeric(df["link_count"], errors="coerce")
df = df.dropna(subset=["link_count"])

# -----------------------------------------
# ORIGINAL CSV stats
orig_min = df["link_count"].min()
orig_max = df["link_count"].max()
orig_avg = df["link_count"].mean()

print("Original CSV statistics:")
print(f"Min: {orig_min}")
print(f"Max: {orig_max}")
print(f"Avg: {orig_avg}")

# -----------------------------------------
# Compute Q3 threshold
q3 = df["link_count"].quantile(0.75)

# Filter Q3–Q4 (>= Q3)
df_q3_q4 = df[df["link_count"] >= q3]

# Q3–Q4 stats
q_min = df_q3_q4["link_count"].min()
q_max = df_q3_q4["link_count"].max()
q_avg = df_q3_q4["link_count"].mean()

print("\nQ3–Q4 statistics (>= 75th percentile):")
print(f"Min: {q_min}")
print(f"Max: {q_max}")
print(f"Avg: {q_avg}")
