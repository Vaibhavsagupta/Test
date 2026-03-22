import os
import json
import zstandard as zstd
from pathlib import Path
from datetime import datetime, timedelta
from app.config import settings
from app.processing.cleaner import clean_data
from app.processing.intent import intent_filter
from app.processing.semantic import semantic_match
from app.processing.scorer import score_records
from app.processing.deduplicator import deduplicate
from app.enrichment.llm_reason import enrich_leads
from app.storage.prod_db import store_prod, is_file_processed, log_file_processed

# 1. Load Clients Config
def load_clients():
    with open(settings.CLIENTS_CONFIG_PATH, 'r') as f:
        return json.load(f)

# 2. Extract Data from ZST Stream for ALL clients at once (OPTIMIZED)
def stream_zst_bulk(file_path, all_clients, limit_per_client=10000):
    print(f"⛏️ [BULK INGEST] Reading {file_path.name} for ALL clients...")
    
    # Pre-calculate keywords for all clients
    client_filters = {}
    for name, config in all_clients.items():
        client_filters[name] = {
            "keywords": [k.lower() for k in config.get("keywords", []) + config.get("icp", [])],
            "candidates": [],
            "done": False
        }
    
    # 6-12 months ago (Requirement: "last 6 months only")
    min_timestamp = int((datetime.now() - timedelta(days=180)).timestamp())
    
    dctx = zstd.ZstdDecompressor()
    active_clients = len(all_clients)
    
    try:
        with open(file_path, 'rb') as fh:
            with dctx.stream_reader(fh) as reader:
                import io
                text_stream = io.TextIOWrapper(reader, encoding='utf-8')
                for i, line in enumerate(text_stream):
                    try:
                        data = json.loads(line)
                        
                        created_utc = data.get("created_utc")
                        if isinstance(created_utc, str): created_utc = int(created_utc)
                        if created_utc and created_utc < min_timestamp: continue

                        body = data.get("body") or data.get("selftext") or ""
                        title = data.get("title", "")
                        content = (title + " " + body).lower()
                        if not content or content in ["[deleted]", "[removed]"]: continue
                        
                        for name, meta in client_filters.items():
                            if meta["done"]: continue
                            
                            if any(kw in content for kw in meta["keywords"]):
                                record = {
                                    "comment_id": data.get("id"),
                                    "post_id": data.get("link_id") or data.get("id"),
                                    "comment": title + " " + body if title else body,
                                    "subreddit": data.get("subreddit"),
                                    "score": data.get("score", 0),
                                    "created_utc": created_utc,
                                    "source_file": file_path.name
                                }
                                meta["candidates"].append(record)
                                
                                if len(meta["candidates"]) >= limit_per_client:
                                    print(f"   ✅ [STREAM] {name} reached limit in this file.")
                                    meta["done"] = True
                                    active_clients -= 1
                        
                        if active_clients <= 0: break
                        if i % 100000 == 0 and i > 0:
                            print(f"   ... scanned {i} lines in {file_path.name}")
                            
                    except Exception:
                        continue
    except Exception as e:
        print(f"❌ [ERROR] Failed to read {file_path.name}: {e}")
    
    return {name: meta["candidates"] for name, meta in client_filters.items()}

# 3. Main Runner
def run_bulk_ingestion():
    all_clients = load_clients()
    zst_files = sorted(list(Path(".").glob("*.zst")))
    
    if not zst_files:
        print("❌ [ERROR] No .zst files found in current directory.")
        return

    print(f"🌕 [START OPTIMIZED] Processing {len(zst_files)} Large Reddit Dumps for {len(all_clients)} Clients...")
    
    total_files = len(zst_files)
    total_clients = len(all_clients)
    total_tasks = total_files * total_clients
    task_count = 0
    start_time = datetime.now().isoformat()

    for file_idx, zst_file in enumerate(zst_files):
        # INCREMENTAL CHECK
        if is_file_processed(zst_file.name):
            print(f"   ⏩ [SKIP] {zst_file.name} was already processed. Skipping to save time.")
            task_count += total_clients
            continue

        # 1. Read ZST ONCE for all clients
        bulk_data = stream_zst_bulk(zst_file, all_clients)
        
        # 2. Process each client's data through the pipeline
        for client_name, raw_data in bulk_data.items():
            task_count += 1
            # Update progress file
            progress = {
                "current_file": zst_file.name,
                "current_client": client_name,
                "files_completed": task_count - 1,
                "total_files": total_tasks,
                "start_time": start_time,
                "percent": round((task_count - 1) / total_tasks * 100, 2)
            }
            with open(".ingest_progress.json", "w") as f:
                json.dump(progress, f)

            if not raw_data:
                print(f"   ⏩ [SKIP] No matches for {client_name} in {zst_file.name}")
                continue
                
            print(f"   💎 [PIPELINE] Processing {len(raw_data)} candidates for {client_name}...")
            clean_records = clean_data(raw_data)
            semantic_scored = semantic_match(clean_records, client_name=client_name)
            filtered = intent_filter(semantic_scored, threshold=0.05)
            scored = score_records(filtered)
            deduped = deduplicate(scored)
            enriched = enrich_leads(deduped, top_n=500)
            
            if enriched:
                store_prod(enriched, client_name=client_name)
                print(f"   🚀 [SUCCESS] Stored {len(enriched)} leads for {client_name} from {zst_file.name}")

        # LOG COMPLETION OF FILE
        log_file_processed(zst_file.name)

    if os.path.exists(".ingest_progress.json"):
        os.remove(".ingest_progress.json")

    print("\n✅ [FINISH] Global Historical Ingestion Complete!")

if __name__ == "__main__":
    run_bulk_ingestion()
