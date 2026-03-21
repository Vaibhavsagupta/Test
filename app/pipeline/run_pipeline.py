import os
import json
import time
from app.config import settings
from app.ingestion.downloader import download_file, fetch_from_arctic_shift
from app.ingestion.duckdb_engine import query_comments, query_submissions
from app.processing.cleaner import clean_data
from app.processing.intent import intent_filter
from app.processing.semantic import semantic_match
from app.processing.scorer import score_records
from app.processing.deduplicator import deduplicate
from app.enrichment.llm_reason import enrich_leads
from app.storage.local_db import store_local
from app.storage.prod_db import store_prod
from app.utils.tracker import is_file_processed, mark_file_processed

def run(subreddit="HairTransplants", client_name="hair_clinic"):
    print(f"🚀 [PIPELINE] Starting Historical Mining for r/{subreddit}...")
    
    # Check if this subreddit/file has been processed already
    # (Using subreddit name as a proxy for the 'file' in this API-based mode)
    tracker_key = f"{subreddit}_{int(time.time() // 86400)}" # Daily tracker
    if is_file_processed(tracker_key):
        print(f"⏹️ [PIPELINE] Skipping r/{subreddit} - already processed today.")
        return []

    # 1. Fetch data for this specific topic
    # For now fetching last 5000 records from PullPush Mirror
    dumps_path = settings.RAW_DIR / f"{subreddit}_comments.jsonl"
    submissions_path = settings.RAW_DIR / f"{subreddit}_submissions.jsonl"
    
    # Trigger download
    fetch_from_arctic_shift(subreddit, str(dumps_path))
    fetch_from_arctic_shift(subreddit, str(submissions_path))

    # 2. Extract using Enhanced DuckDB Engine (Phases 1-2)
    # The engine now handles 6-mo filtering and subreddit matching at SQL level
    comments_data = query_comments(dumps_path.as_posix(), client_name=client_name)
    posts_data = query_submissions(submissions_path.as_posix(), client_name=client_name)
    
    data = comments_data + posts_data
    if not data:
        print(f"⚠️ No new data found in r/{subreddit} passing early filters.")
        mark_file_processed(tracker_key) # Don't retry empty subs today
        return []

    # 3. Clean and Filter
    clean_records = clean_data(data)
    filtered = intent_filter(clean_records)
    
    # 4. Semantic Match (MiniLM)
    semantic_scored = semantic_match(filtered, client_name=client_name)
    
    # 5. Score (Semantic + Intent + Engagement + Recency)
    scored = score_records(semantic_scored)
    
    # 6. Deduplicate and Enrich (LLM)
    deduped = deduplicate(scored)
    
    # Only process top 50 results through LLM (Phase 4)
    enriched = enrich_leads(deduped, top_n=50)
    
    # 7. Store results
    store_prod(enriched)
    
    # 8. Mark as processed (Phase 2)
    mark_file_processed(tracker_key)
    
    print(f"✅ [FINAL] r/{subreddit} mining complete! {len(enriched)} leads found and stored.")
    return enriched

if __name__ == "__main__":
    run()
