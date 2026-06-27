import pandas as pd
import re

# Read your CSV file
df = pd.read_csv("combined.csv")

# Keep only rows where isGithub == True
df_true = df[df["isGithub"] == True].copy()

# Function to classify GitHub link type
def get_github_link_type(url):
    if not isinstance(url, str):
        return "unknown"
    url = url.lower()

    patterns = [
        (r'/pull/\d+', "pull_request"),
        (r'/issues/\d+', "issue"),
        (r'/discussions/\d+', "discussion"),
        (r'/commit/[0-9a-f]+', "commit"),
        (r'/compare/', "compare"), 
        (r'/tree/[^/]+', "branch_or_tree"),
        (r'/blob/', "file"),
        (r'/releases?', "release"),
        (r'/tags?', "tag"),
        (r'/actions/', "actions"),
        (r'/wiki/', "wiki"),
        (r'/projects?/', "project"),
        (r'/packages?', "package"),
        (r'/marketplace/', "marketplace"),
        (r'github\.com/[^/]+/[^/]+/?$', "repository"),
        (r'github\.com/[^/]+/?$', "profile_or_org"),
    ]

    for pattern, label in patterns:
        if re.search(pattern, url):
            return label
    return "other"

# Apply classification to create a new column
df_true["github_type"] = df_true["link"].apply(get_github_link_type)

# Save the filtered + classified data to a new CSV file
output_file = "github_links.csv"
df_true.to_csv(output_file, index=False)

# Print summary
print(f"✅ Saved {len(df_true)} GitHub links to '{output_file}'")
print("\nGitHub Link Type Counts:")
print(df_true["github_type"].value_counts())
