import os
import requests
import json
import zstandard as zstandard
import time

def fetch_from_arctic_shift(subreddit=None, save_path=None, limit=10000, query=None):
    """
    Automated fetch from PullPush/Pushshift Mirror API to get LAST 12 MONTHS.
    Includes PAGINATION and Keyword Support (q).
    """
    scope = f"r/{subreddit}" if subreddit else "ALL subreddits"
    topic = f"keyword '{query}'" if query else "latest posts"
    print(f"[DOWNLOADER] Fetching 12-month depth for {topic} in {scope}...")
    
    # Filter for last 12 months
    one_year_ago = int(time.time()) - (365 * 24 * 60 * 60)
    data_type = "comment" if save_path and "comments" in save_path.lower() else "submission"
    url = f"https://api.pullpush.io/reddit/search/{data_type}/"
    
    all_data = []
    before = None # For pagination
    CHUNK_SIZE = 500 # API friendly size
    
    try:
        while len(all_data) < limit:
            params = {
                "size": CHUNK_SIZE,
                "after": one_year_ago,
                "sort": "desc"
            }
            if subreddit: params["subreddit"] = subreddit
            if query: params["q"] = query
            
            if before:
                params["before"] = before

                
            r = requests.get(url, params=params, timeout=60)
            r.raise_for_status()
            batch = r.json().get("data", [])
            
            if not batch:
                break
                
            all_data.extend(batch)
            print(f"[DOWNLOADER] Got {len(all_data)} records so far...")
            
            # Use timestamp of last record for next page
            before = batch[-1].get("created_utc")
            
            # Rate limiting safety
            time.sleep(1.0) # Increased to 1.0 safely for bulk


        if not all_data:
            print(f"[DOWNLOADER] No data found for {subreddit} in the last 12 months.")
            return None

        print(f"[DOWNLOADER] Successfully gathered {len(all_data)} records for {subreddit}.")
        
        with open(save_path, 'w', encoding='utf-8') as f:
            for item in all_data:
                f.write(json.dumps(item) + "\n")
                    
        print(f"[DOWNLOADER] saved to {save_path}")
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

