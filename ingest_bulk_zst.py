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

def load_configs():
    with open(settings.CLIENTS_CONFIG_PATH, 'r') as f:
        return json.load(f)

def stream_zst_bulk(file_path, clients, limit_per_client=10000):
    # just a quick check on how much data we're pulling
    print(f"reading {file_path.name} to find matches for all clients")
    
    filters = {}
    for name, cfg in clients.items():
        filters[name] = {
            "keywords": [k.lower() for k in cfg.get("keywords", []) + cfg.get("icp", [])],
            "candidates": [],
            "done": False
        }
    
    # requirements say last 6 months only
    min_timestamp = int((datetime.now() - timedelta(days=180)).timestamp())
    
    dctx = zstd.ZstdDecompressor()
    active_count = len(clients)
    
    try:
        with open(file_path, 'rb') as fh:
            with dctx.stream_reader(fh) as reader:
                import io
                text_stream = io.TextIOWrapper(reader, encoding='utf-8')
                for i, line in enumerate(text_stream):
                    try:
                        data = json.loads(line)
                        
                        ts = data.get("created_utc")
                        if isinstance(ts, str): ts = int(ts)
                        if ts and ts < min_timestamp:
                            continue # skip old stuff

                        body = data.get("body") or data.get("selftext") or ""
                        title = data.get("title", "")
                        content = (title + " " + body).lower()
                        
                        # basic noise filtering
                        if not content or content in ["[deleted]", "[removed]"]:
                            continue
                        
                        for name, meta in filters.items():
                            if meta["done"]:
                                continue
                            
                            if any(kw in content for kw in meta["keywords"]):
                                record = {
                                    "comment_id": data.get("id"),
                                    "post_id": data.get("link_id") or data.get("id"),
                                    "comment": title + " " + body if title else body,
                                    "subreddit": data.get("subreddit"),
                                    "score": data.get("score", 0),
                                    "created_utc": ts,
                                    "source_file": file_path.name
                                }
                                meta["candidates"].append(record)
                                
                                if len(meta["candidates"]) >= limit_per_client:
                                    print(f"quota reached for {name} in this file")
                                    meta["done"] = True
                                    active_count -= 1
                        
                        if active_count <= 0:
                            break
                            
                        if i % 100000 == 0 and i > 0:
                            print(f"scanned {i} lines so far...")
                            
                    except Exception:
                        continue
    except Exception as e:
        print(f"error reading {file_path.name}: {e}")
    
    return {name: meta["candidates"] for name, meta in filters.items()}

def run_bulk_ingestion():
    configs = load_configs()
    zst_files = sorted(list(Path(".").glob("*.zst")))
    
    if not zst_files:
        print("no .zst files found here")
        return

    print(f"starting ingest for {len(zst_files)} files across {len(configs)} clients")
    
    total_files = len(zst_files)
    total_clients = len(configs)
    total_tasks = total_files * total_clients
    count = 0
    start_time = datetime.now().isoformat()

    for zst_file in zst_files:
        if is_file_processed(zst_file.name):
            print(f"skipping {zst_file.name} (already done)")
            count += total_clients
            continue

        # process the file once for everyone
        raw_data_map = stream_zst_bulk(zst_file, configs)
        
        for name, raw_data in raw_data_map.items():
            count += 1
            
            # update local progress just in case we crash
            progress = {
                "current_file": zst_file.name,
                "current_client": name,
                "files_completed": count - 1,
                "total_files": total_tasks,
                "start_time": start_time,
                "percent": round((count - 1) / total_tasks * 100, 2)
            }
            with open(".ingest_progress.json", "w") as f:
                json.dump(progress, f)

            if not raw_data:
                continue
                
            print(f"processing {len(raw_data)} hits for {name}")
            
            # standard pipeline flow
            clean = clean_data(raw_data)
            semantic = semantic_match(clean, client_name=name)
            filtered = intent_filter(semantic, threshold=0.05)
            scored = score_records(filtered)
            deduped = deduplicate(scored)
            results = enrich_leads(deduped, top_n=500)
            
            if results:
                store_prod(results, client_name=name)
                print(f"saved {len(results)} new leads for {name}")

        # mark this file as finished
        log_file_processed(zst_file.name)

    if os.path.exists(".ingest_progress.json"):
        os.remove(".ingest_progress.json")

    print("all done with the bulk ingestion")

if __name__ == "__main__":
    run_bulk_ingestion()
