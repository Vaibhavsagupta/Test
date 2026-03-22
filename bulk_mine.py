from app.pipeline.run_pipeline import run
import json
import time

# load up the client list from config
config_path = r"c:/Users/Vaibhav/Desktop/test-2/app/config/clients.json"
with open(config_path, "r") as f:
    clients = json.load(f)

print(f"Loading {len(clients)} clients for historical mining...")

for name, cfg in clients.items():
    print(f"--- processing {name} ---")
    
    # hit every subreddit for this client
    subreddits = cfg.get("subreddits", [])
    if subreddits:
        print(f"found {len(subreddits)} subreddits to scrape")
        
    for sub in subreddits:
        try:
            print(f"mining r/{sub} for the last 12 months")
            run(subreddit=sub, client_name=name)
            
            # small delay so we don't blow up memory
            time.sleep(10)
        except Exception as e:
            print(f"failed to mine {sub}: {e}")

    # now go through individual keywords and ICP terms
    # requirements say we need both
    keywords = cfg.get("keywords", []) + cfg.get("icp", [])
    if keywords:
        print(f"starting reddit-wide search for {len(keywords)} keywords")
        
    for kw in keywords:
        try:
            print(f"searching for '{kw}' (12mo depth)")
            # subreddit=None means we search all of reddit
            run(subreddit=None, client_name=name, query=kw)
            
            # another sleep just in case
            time.sleep(10)
        except Exception as e:
            print(f"skipped keyword '{kw}' due to error: {e}")

print("done with all historical data extraction")
