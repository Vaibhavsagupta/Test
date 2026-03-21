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
def run_historical_pipeline(subreddit: str = "HairTransplants"):
    """ Task 3: Trigger the Background Historical Lead Generation Pipeline for ANY subreddit. """
    from app.pipeline.run_pipeline import run as trigger_pipeline
    
    # Run in background
    thread = threading.Thread(target=trigger_pipeline, kwargs={"subreddit": subreddit})
    thread.start()
    return {"message": f"Pipeline triggered for r/{subreddit}. Mining pichle 12 mahine ka data."}


@router.get("/historical-leads")
def get_historical_leads(
    subreddit: str = None, 
    client: str = None, 
    date: str = None, # Simple YYYY-MM-DD
    limit: int = 50
):
    """ Task 3: Get leads extracted from the historical dataset previously processed. """
    # Unified path in data/processed
    db_path = Path("data/processed/prod.sqlite").resolve()

    if not db_path.exists():
        return {"message": "No historical data found. Try running /run-historical-pipeline first!"}
        
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM leads WHERE 1=1"
    params = []
    
    if subreddit:
        query += " AND LOWER(subreddit) = LOWER(?)"
        params.append(subreddit)
        
    if date:
        # Simple date to epoch conversion (Start of Day)
        import datetime
        try:
            epoch = int(datetime.datetime.strptime(date, "%Y-%m-%d").timestamp())
            query += " AND created_utc >= ?"
            params.append(epoch)
        except ValueError:
            pass # Invalid date format ignore
            
    # Client filtering in this schema is linked to subreddit lists from config
    # For now we filter results by what's in the DB
        
    query += " ORDER BY final_score DESC LIMIT ?"
    params.append(limit)
    
    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        result = []
        for r in rows:
            result.append({
                "post_id": r["post_id"],
                "subreddit": r["subreddit"],
                "comment": r["comment"],
                "score": r["score"],
                "intent": r["intent"],
                "final_score": r["final_score"],
                "reason": r["reason"],
                "permalink": r["permalink"],
                "created_utc": r["created_utc"]
            })


            
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()
        
    return {
        "lead_count": len(result),
        "leads": result
    }

