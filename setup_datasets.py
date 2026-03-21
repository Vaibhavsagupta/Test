import os
import requests
import pandas as pd

# Directories
RAW_DIR = "data/raw"
INTERIM_DIR = "data/interim"
PROCESSED_DIR = "data/processed"

# URLs
RELATIONS_URL = "https://snap.stanford.edu/data/soc-redditHyperlinks-body.tsv"
SUBREDDITS_EMB_URL = "https://snap.stanford.edu/data/web-redditEmbeddings-subreddits.csv"
METADATA_URL = "https://raw.githubusercontent.com/TheShadow29/subreddit-classification-dataset/master/req_subreddits.csv"
PUSHSHIFT_SAMPLE_URL = "https://raw.githubusercontent.com/luminati-io/Reddit-dataset-samples/main/Reddit-%20Posts.csv"

def download_file(url, target_path):
    if os.path.exists(target_path):
        print(f"File already exists: {target_path}")
        return
    print(f"Downloading {url} to {target_path}...")
    try:
        response = requests.get(url, stream=True, timeout=30)
        if response.status_code == 200:
            with open(target_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"Successfully downloaded {target_path}")
        else:
            print(f"Failed to download {url}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

if __name__ == "__main__":
    # Ensure dirs exist
    for d in [RAW_DIR, INTERIM_DIR, PROCESSED_DIR]:
        os.makedirs(d, exist_ok=True)

    # Download
    download_file(RELATIONS_URL, os.path.join(RAW_DIR, "reddit_links.tsv"))
    download_file(SUBREDDITS_EMB_URL, os.path.join(RAW_DIR, "subreddit_embeddings_names.csv"))
    download_file(METADATA_URL, os.path.join(RAW_DIR, "subreddits_metadata.csv"))
    download_file(PUSHSHIFT_SAMPLE_URL, os.path.join(RAW_DIR, "pushshift_sample.csv"))
    
    print("Download phase complete.")
