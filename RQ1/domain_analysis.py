import pandas as pd
from urllib.parse import urlparse

def perform_domain_analysis(csv_file_path, output_txt_path='domain_analysis_report.txt'):
    # 1. Load the CSV file
    try:
        df = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        print(f"Error: The file at {csv_file_path} was not found.")
        return
    
    # 2. Robustly handle 'isGithub' column booleans
    if df['isGithub'].dtype == 'object':
        df['isGithub'] = df['isGithub'].astype(str).str.strip().str.lower().map({'true': True, 'false': False})
    
    # 3. Filter for rows where isGithub is False and link is not null
    filtered_df = df[df['isGithub'] == False].dropna(subset=['link']).copy()
    
    # Get the total row count of matching records
    total_matching_rows = len(filtered_df)
    
    if total_matching_rows == 0:
        print("No records found where 'isGithub' is False.")
        return

    # 4. Extract the domain (hostname) from each link
    def extract_domain(url):
        try:
            hostname = urlparse(str(url)).netloc
            if hostname.startswith('www.'):
                hostname = hostname[4:]
            return hostname if hostname else "Invalid/Empty URL"
        except Exception:
            return "Parsing Error"

    filtered_df['domain'] = filtered_df['link'].apply(extract_domain)

    # 5. Perform Analysis (Counts and Percentages)
    domain_counts = filtered_df['domain'].value_counts()
    domain_percentages = filtered_df['domain'].value_counts(normalize=True) * 100

    # 6. Format and save the output to a text file
    with open(output_txt_path, 'w', encoding='utf-8') as f:
        f.write("=== DOMAIN ANALYSIS REPORT ===\n")
        f.write(f"Total number of rows analyzed (isGithub is False): {total_matching_rows}\n\n")
        f.write("Domain Distribution:\n")
        f.write("-" * 50 + "\n")
        f.write(f"{'Domain':<30} {'Count':<10} {'Percentage (%)':<15}\n")
        f.write("-" * 50 + "\n")
        
        for domain, count in domain_counts.items():
            percentage = domain_percentages[domain]
            f.write(f"{domain:<30} {count:<10} {percentage:<15.2f}%\n")
            
        f.write("-" * 50 + "\n")

    print(f"Analysis complete. Report saved to: {output_txt_path}")

# Example Usage:
perform_domain_analysis('combined.csv', 'my_report.txt')