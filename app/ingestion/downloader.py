import os
import requests
import json
import zstandard as zstandard
import time

def fetch_from_arctic_shift(subreddit, save_path, limit=5000):
    """
    Automated fetch from PullPush/Pushshift Mirror API to get LAST 12 MONTHS.
    Saves as .jsonl for DuckDB mining.
    """
    print(f"[DOWNLOADER] Fetching {subreddit} data from PullPush API Mirror...")
    
    # Filter for last 12 months
    one_year_ago = int(time.time()) - (365 * 24 * 60 * 60)
    
    # PullPush endpoint
    data_type = "comment" if "comments" in save_path.lower() else "submission"
    url = f"https://api.pullpush.io/reddit/search/{data_type}/"
    
    params = {
        "subreddit": subreddit,
        "limit": limit,
        "after": one_year_ago,
        "sort": "desc"
    }
    
    try:
        r = requests.get(url, params=params, timeout=60)
        r.raise_for_status()
        data = r.json().get("data", [])
        
        if not data:
            print(f"[DOWNLOADER] No data found for {subreddit} in the last 12 months.")
            return None

        print(f"[DOWNLOADER] Received {len(data)} records for {subreddit}.")
        
        with open(save_path, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item) + "\n")
                    
        print(f"[DOWNLOADER] Saved to {save_path}")
        return save_path
    except Exception as e:
        print(f"[DOWNLOADER ERROR] {e}")
        return None



def download_file(url, save_path):
    # Legacy direct download mode (unused if using API fallback)
    if os.path.exists(save_path):
        return save_path
    r = requests.get(url, stream=True, verify=False)
    r.raise_for_status()
    with open(save_path, 'wb') as f:
        for chunk in r.iter_content(1024*1024):
            f.write(chunk)
    return save_path

