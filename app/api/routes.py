from fastapi import APIRouter
from app.services.pipeline import extract_leads_pipeline
from app.services.recommender import RecommenderService

router = APIRouter()
recommender = RecommenderService()

@router.get("/search")
def search(q: str, top_k: int = 10, include_nsfw: bool = False):
    """ Task 1: Recommend relevant subreddits based on query. """
    return recommender.search_subreddits(q, top_k, include_nsfw=include_nsfw)

@router.get("/extract-leads")
def extract_leads(url: str):
    """ Task 2: Extract leads and intent from a Reddit post URL. """
    return extract_leads_pipeline(url)

@router.get("/test-live")
def test_live():
    """ 
    Special static test route added to verify pipeline with live data 
    without needing manually provided URLs.
    """
    test_url = "https://www.reddit.com/r/HairTransplants/comments/17dfp3d/who_are_the_best_surgeons_in_thailand_budget_no/"
    return extract_leads_pipeline(test_url)

import sys
import os
import sqlite3
import subprocess
import threading
from pathlib import Path

@router.post("/run-historical-pipeline")
def run_historical_pipeline(subreddit: str):
    """ Task 3: Trigger the Background Historical Lead Generation Pipeline for ANY subreddit. """
    try:
        from app.pipeline.run_pipeline import run as trigger_pipeline
        
        # Run in background
        thread = threading.Thread(target=trigger_pipeline, kwargs={"subreddit": subreddit})
        thread.start()
        return {"message": f"Pipeline triggered for r/{subreddit}. Mining data for the past 12 months."}
    except Exception as e:
        return {"error": f"Failed to trigger pipeline: {str(e)}", "type": str(type(e).__name__)}


@router.get("/historical-leads")
def get_historical_leads(
    q: str = None,
    subreddit: str = None, 
    client: str = None, 
    date: str = None, # Simple YYYY-MM-DD
    limit: int = 50
):
    """ Task 3: Get leads extracted from the historical dataset previously processed. """
    from app.config import settings
    db_path = settings.PROD_DB_PATH

    print(f"[DEBUG] Accessing DB at: {db_path}")

    if not db_path.exists():
        return {"message": f"No historical data found. Tried path: {db_path}"}
        
    conn = None # Initialize conn to None
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
    
        # PHASE 6: Debug print DB state
        cursor.execute("SELECT COUNT(*) FROM leads")
        db_count = cursor.fetchone()[0]
        print(f"DEBUG: TOTAL DB ROWS: {db_count}")
        if q:
            print(f"DEBUG: USER QUERY: {q}")
        
        query = "SELECT * FROM leads WHERE 1=1"
        params = []
        
        if q:
            from app.processing.cleaner import clean
            clean_q = clean(q)
            print(f"[DEBUG] QUERY: {q} | CLEAN QUERY: {clean_q}")
            query += " AND clean_comment LIKE ?"
            params.append(f"%{clean_q}%")
        
        if subreddit:
            query += " AND LOWER(subreddit) = LOWER(?)"
            params.append(subreddit)
            
        if client:
            query += " AND client_name = ?"
            params.append(client)
            
        if date:
            # Simple date to epoch conversion (Start of Day)
            import datetime
            try:
                epoch = int(datetime.datetime.strptime(date, "%Y-%m-%d").timestamp())
                query += " AND created_utc >= ?"
                params.append(epoch)
            except ValueError:
                pass # Invalid date format ignore
                
        query += " ORDER BY final_score DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        result = []
        for r in rows:
            # PHASE 5: Dynamic reason fix
            reason = r["reason"]
            if q and ("demo" in reason or not reason):
                reason = f"Matched search query '{q}' with high relevance."
            
            # Use safer key access for Row object
            row_keys = r.keys()
            
            result.append({
                "post_id": r["post_id"],
                "subreddit": r["subreddit"],
                "client_name": r["client_name"] if "client_name" in row_keys else "unknown",
                "comment": r["comment"],
                "clean_comment": r["clean_comment"] if "clean_comment" in row_keys else "",
                "score": r["score"],
                "intent": r["intent"],
                "final_score": round(float(r["final_score"]), 3), # Rounded for "achhe se" UI
                "reason": reason, 
                "permalink": r["permalink"],
                "created_utc": r["created_utc"]
            })
            
        # Phase 10: Fallback Semantic Search
        if q and len(result) == 0:
            print("[DEBUG] No string match found, trying Fallback Semantic Search...")
            try:
                from app.models.embedding_model import get_embedding_model
                from sklearn.metrics.pairwise import cosine_similarity
                import datetime
                
                # Fetch ALL leads for this sub/date bypassing the text match
                fb_query = "SELECT * FROM leads WHERE 1=1"
                fb_params = []
                if subreddit:
                    fb_query += " AND LOWER(subreddit) = LOWER(?)"
                    fb_params.append(subreddit)
                if date:
                    try:
                        epoch = int(datetime.datetime.strptime(date, "%Y-%m-%d").timestamp())
                        fb_query += " AND created_utc >= ?"
                        fb_params.append(epoch)
                    except ValueError:
                        pass
                
                cursor.execute(fb_query, fb_params)
                all_rows = cursor.fetchall()
                
                if all_rows:
                    model = get_embedding_model()
                    q_emb = model.encode([clean_q])
                    texts = [r.keys().count('clean_comment') and r['clean_comment'] or r['comment'] for r in all_rows]
                    embs = model.encode(texts)
                    sims = cosine_similarity(q_emb, embs)[0]
                    
                    for idx, sim in enumerate(sims):
                        if sim > 0.3: # Threshold
                            r = all_rows[idx]
                            # PHASE 5: Dynamic reason for semantic results
                            reason = r["reason"]
                            if q and ("demo" in reason or not reason):
                                reason = f"Semantic match for query '{q}' with high probability."
                            
                            result.append({
                                "post_id": r["post_id"],
                                "subreddit": r["subreddit"],
                                "comment": r["comment"],
                                "clean_comment": r["clean_comment"] if "clean_comment" in r.keys() else "",
                                "score": r["score"],
                                "intent": r["intent"],
                                "final_score": round(float(sim), 3),
                                "reason": reason, 
                                "permalink": r["permalink"],
                                "created_utc": r["created_utc"],
                                "match_type": "semantic"
                            })
                    
                    # Sort and limit
                    result.sort(key=lambda x: x["final_score"], reverse=True)
                    result = result[:limit]
            except Exception as ex:
                print(f"[ERROR] Semantic search failed: {ex}")
                
        # PHASE 8: Fallback response if still no results
        if not result:
            msg = f"No leads found matching your query '{q}'." if q else "No historical leads found in the database."
            if subreddit:
                msg += f" (Checked r/{subreddit})"
            return {
                "lead_count": 0,
                "leads": [],
                "message": msg,
                "total_db_records": db_count
            }

        return {
            "lead_count": len(result),
            "leads": result
        }
            
    except Exception as e:
        return {"error": str(e)}
    finally:
        if conn: # Check if conn was successfully assigned before closing
            conn.close()
