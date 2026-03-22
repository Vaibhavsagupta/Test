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
    """ main entry point for running the historical data pipeline """
    print(f"starting mining process for r/{subreddit}")
    
    # tracker to make sure we don't double process
    tracker_key = f"{subreddit}_{int(time.time() // 86400)}"
    
    # fetch the actual data
    # files go into raw directory specified in settings
    dumps_path = settings.RAW_DIR / f"{subreddit}_comments.jsonl"
    submissions_path = settings.RAW_DIR / f"{subreddit}_submissions.jsonl"
    
    # increased limits to get a full 12 month depth for this sub/query
    c_path = fetch_from_arctic_shift(subreddit, str(dumps_path), limit=12000, query=query)
    s_path = fetch_from_arctic_shift(subreddit, str(submissions_path), limit=4000, query=query)

    if not c_path:
        print("fetch failed, using demo/empty files to keep things moving")
        dumps_path.touch()
        submissions_path.touch()

    # extract data using duckdb - this handles the 6-mo filtering for us
    comments = query_comments(dumps_path.as_posix(), client_name=client_name, target_subreddit=subreddit)
    posts = query_submissions(submissions_path.as_posix(), client_name=client_name, target_subreddit=subreddit)
    
    print(f"debug: found {len(comments)} comments and {len(posts)} posts")

    data = comments + posts
    if not data:
        print(f"no new data found for r/{subreddit} passing initial filters")
        mark_file_processed(tracker_key)
        return []

    # cleansing and basic filtering
    clean = clean_data(data)
    
    # semantic matching via MiniLM
    # check similarity across all leads even multilingual ones
    semantic = semantic_match(clean, client_name=client_name)
    
    # intent filtering - keep anything above 0.02 threshold
    filtered = intent_filter(semantic, threshold=0.02)
    
    # final scoring based on multiple factors (engagement, recency, etc)
    scored = score_records(filtered)
    
    # deduplicate and then enrich with LLM
    deduped = deduplicate(scored)
    
    # just enrich the top 50, otherwise it's too expensive/slow
    enriched = enrich_leads(deduped, top_n=50)
    
    if not enriched:
        print("no real leads identified, skipping storage")
        return []
    
    # save to prod db
    store_prod(enriched)
    mark_file_processed(tracker_key)
    
    print(f"mining finished for r/{subreddit}. found {len(enriched)} leads.")
    return enriched

if __name__ == "__main__":
    run()
