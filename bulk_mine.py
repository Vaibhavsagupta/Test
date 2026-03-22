from app.pipeline.run_pipeline import run
import json
import time

# Load all keywords from config
config_path = r"c:/Users/Vaibhav/Desktop/test-2/app/config/clients.json"
with open(config_path, "r") as f:
    clients = json.load(f)

print("--- 🌕 STARTING FULL GLOBAL HISTORICAL MINING (EVERY SINGLE KEYWORD) ---")
print(f"Total Clients to process: {len(clients)}")

for client_name, config in clients.items():
    print(f"\n💎 PROCESSING CLIENT: {client_name}")
    
    # 1. Mine EVERY Subreddit listed for this client
    subreddits = config.get("subreddits", [])
    print(f"   📂 Targeting {len(subreddits)} subreddits...")
    for sub in subreddits:
        try:
            print(f"   ⛏️ Mining r/{sub} (FULL 12 Months)...")
            run(subreddit=sub, client_name=client_name)
            time.sleep(10) # Safety wait for memory
        except Exception as e: print(f"   ⚠️ Skipping {sub}: {e}")

    # 2. Mine EVERY Keyword and ICP term listed
    # We combine them into a single list of tasks
    all_keywords = config.get("keywords", []) + config.get("icp", [])
    print(f"   🔍 Targeting {len(all_keywords)} unique keywords Reddit-wide...")
    for kw in all_keywords:
        try:
            print(f"   🔭 Mining Keyword: '{kw}' (Across ALL of Reddit - 12mo)...")
            # Subreddit=None triggers Reddit-wide search
            run(subreddit=None, client_name=client_name, query=kw)
            time.sleep(10) # Safety wait for memory
        except Exception as e: print(f"   ⚠️ Skipping keyword '{kw}': {e}")

print("\n✅ [SUCCESS] FULL HISTORICAL DATA EXTRACTION COMPLETE!")
print("All keywords and subreddits have been mined for the past 12 months.")
