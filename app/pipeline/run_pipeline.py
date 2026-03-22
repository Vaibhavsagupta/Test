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

def run(subreddit="HairTransplants", client_name="hair_clinic", query=None):
    print(f"🚀 [PIPELINE] Starting Historical Mining for r/{subreddit}...")
    
    # Check if this subreddit/file has been processed already
    tracker_key = f"{subreddit}_{int(time.time() // 86400)}" # Daily tracker
    # if is_file_processed(tracker_key):
    #     print(f"⏹️ [PIPELINE] Skipping r/{subreddit} - already processed today.")
    #     return []

    # 1. Fetch data for this specific topic
    # For now fetching last 500 records from PullPush Mirror (the mirror shared by USER)
    dumps_path = settings.RAW_DIR / f"{subreddit}_comments.jsonl"
    submissions_path = settings.RAW_DIR / f"{subreddit}_submissions.jsonl"
    
    # Trigger download - INCREASED LIMITS for FULL 12 months depth
    c_path = fetch_from_arctic_shift(subreddit, str(dumps_path), limit=12000, query=query)
    s_path = fetch_from_arctic_shift(subreddit, str(submissions_path), limit=4000, query=query)


    if not c_path:
        print("⚠️ Download failed! Using fallback demo data...")
        # Fallback empty file to allow pipeline to continue with demo leads
        dumps_path.touch()
        submissions_path.touch()

    # 2. Extract using Enhanced DuckDB Engine (Phases 1-2)
    # The engine now handles 6-mo filtering and subreddit matching at SQL level
    comments_data = query_comments(dumps_path.as_posix(), client_name=client_name, target_subreddit=subreddit)
    posts_data = query_submissions(submissions_path.as_posix(), client_name=client_name, target_subreddit=subreddit)
    
    print(f"DEBUG: Found {len(comments_data)} comments via DuckDB.")
    print(f"DEBUG: Found {len(posts_data)} posts via DuckDB.")

    data = comments_data + posts_data
    if not data:
        print(f"⚠️ No new data found in r/{subreddit} passing early filters.")
        mark_file_processed(tracker_key) # Don't retry empty subs today
        # Go to demo data instead of returning early
        # return []

    # 3. Clean and Filter
    clean_records = clean_data(data)
    print(f"DEBUG: {len(clean_records)} records after cleaning.")
    
    # 4. Semantic Match (MiniLM) - DO THIS FIRST to avoid dropping multilingual leads early
    semantic_scored = semantic_match(clean_records, client_name=client_name)
    
    # 5. Intent Filter (AI Similarity)
    # Lowered threshold to 0.02 for bulk leads to be more inclusive of other languages
    filtered = intent_filter(semantic_scored, threshold=0.02)

    
    # 6. Score (Semantic + Intent + Engagement + Recency)
    scored = score_records(filtered)

    
    # 6. Deduplicate and Enrich (LLM)
    deduped = deduplicate(scored)
    
    # Only process top 50 results through LLM (Phase 4)
    enriched = enrich_leads(deduped, top_n=50)
    
    # 7. Store results
    if not enriched:
        print("⚠️ No real leads found. Skipping storage/demo insertion.")
        return []
    
    store_prod(enriched)
    
    # 8. Mark as processed (Phase 2)
    mark_file_processed(tracker_key)
    
    print(f"✅ [FINAL] r/{subreddit} mining complete! {len(enriched)} leads found and stored.")
    return enriched

if __name__ == "__main__":
    run()
