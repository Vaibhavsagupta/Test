import pandas as pd
import os

def inspect_csv(path, sep=None):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return
    print(f"\n--- Inspecting {path} ---")
    try:
        # Try different encodings
        df = pd.read_csv(path, sep=sep, nrows=5, on_bad_lines='skip')
        print("Columns:", df.columns.tolist())
        print("Sample Data:\n", df.head(3))
    except Exception as e:
        print(f"Error reading {path}: {e}")

if __name__ == "__main__":
    for f in ["data/raw/subreddits_metadata.csv", "data/raw/pushshift_sample.csv"]:
        if os.path.exists(f):
            print(f"\n--- {f} ---")
            df = pd.read_csv(f, nrows=1)
            print("Columns:", df.columns.tolist())
            print("First row:", df.iloc[0].to_dict())
