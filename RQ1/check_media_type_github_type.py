import pandas as pd

# 1. Load your CSV file
file_path = 'combined.csv'
df = pd.read_csv(file_path)

# Clean and standardize the 'isGithub' column to boolean values
df['isGithub'] = df['isGithub'].astype(str).str.strip().str.capitalize() == 'True'

# 2. Separate into GitHub and Non-GitHub groups
github_df = df[df['isGithub'] == True]
non_github_df = df[df['isGithub'] == False]

# 3. Calculate breakdown of media_type for GitHub Group
print("=========================================")
print("  MEDIA TYPE BREAKDOWN FOR GITHUB GROUP  ")
print("=========================================")
if not github_df.empty:
    gh_counts = github_df['media_type'].value_counts()
    gh_percentages = github_df['media_type'].value_counts(normalize=True) * 100
    
    for media, count, pct in zip(gh_counts.index, gh_counts.values, gh_percentages.values):
        print(f"Media: {media:<12} | Count: {count:<4} | Percentage: {pct:.2f}%")
else:
    print("No rows found for GitHub group.")

# 4. Calculate breakdown of media_type for Non-GitHub Group
print("\n=========================================")
print("  MEDIA TYPE BREAKDOWN FOR NON-GITHUB GROUP  ")
print("=========================================")
if not non_github_df.empty:
    ngh_counts = non_github_df['media_type'].value_counts()
    ngh_percentages = non_github_df['media_type'].value_counts(normalize=True) * 100
    
    for media, count, pct in zip(ngh_counts.index, ngh_counts.values, ngh_percentages.values):
        print(f"Media: {media:<12} | Count: {count:<4} | Percentage: {pct:.2f}%")
else:
    print("No rows found for Non-GitHub group.")