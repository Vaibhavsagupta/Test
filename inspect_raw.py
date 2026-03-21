
import pandas as pd
import os

RAW_DIR = "data/raw"
csv_path = os.path.join(RAW_DIR, "subreddits_metadata.csv")

if os.path.exists(csv_path):
    print("Loading file...")
    # Use chunksize to avoid memory issues and print columns/values
    df_iter = pd.read_csv(csv_path, engine='python', on_bad_lines='skip', chunksize=100)
    df = next(df_iter)
    print(f"Columns: {df.columns.tolist()}")
    if 'over18' in df.columns:
        print(f"Sample 'over18' values: {df['over18'].unique().tolist()}")
        print(f"First 10 rows 'over18':\n{df[['subreddit_name', 'over18']].head(10)}")
    else:
        print("Column 'over18' not found!")
else:
    print(f"File not found: {csv_path}")
