from datetime import datetime

def score_records(records):
    print(f"[SCORER] Calculating final scores using upgraded weights (0.4/0.2/0.2/0.2)...")
    
    now = int(datetime.now().timestamp())
    MAX_AGE_SECONDS = 180 * 24 * 60 * 60 # 6 months
    
    for r in records:
        # Phase 8: Weight distribution upgraded to include Recency
        # 0.4 * semantic + 0.2 * intent + 0.2 * engagement (score) + 0.2 * recency
        
        semantic = r.get("semantic_score", 0.0)
        intent = r.get("intent_score", 0.0)
        
        # Engagement scaling (Cap at 100 upvotes = 1.0)
        engagement = min(max(0, r.get("score", 0)) / 100.0, 1.0)
        
        # Recency scaling (Newer = 1.0, 180 days old = 0.0)
        created_utc = r.get("created_utc", now)
        age_seconds = now - created_utc
        recency = max(0, 1.0 - (age_seconds / MAX_AGE_SECONDS))
        
        final_score = (
            0.4 * semantic +
            0.2 * intent +
            0.2 * engagement +
            0.2 * recency
        )
        r["recency_score"] = recency
        r["final_score"] = final_score
        
    records.sort(key=lambda x: x["final_score"], reverse=True)
    return records

