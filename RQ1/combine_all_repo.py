import os
import pandas as pd

# Folder containing your CSV files
folder_path = os.getcwd()

# Output file name
output_file = "combined.csv"

# List to hold all DataFrames
dataframes = []

# Loop through all files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".csv"):
        file_path = os.path.join(folder_path, filename)
        print(f"Reading: {filename}")
        df = pd.read_csv(file_path)
        dataframes.append(df)

# Combine all DataFrames
combined_df = pd.concat(dataframes, ignore_index=True)

# Save the combined file
combined_df.to_csv(output_file, index=False)

print(f"✅ Combined {len(dataframes)} CSV files into {output_file}")
