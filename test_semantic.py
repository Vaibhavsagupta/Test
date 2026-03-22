import sqlite3
import os
from app.models.embedding_model import get_embedding_model
from sklearn.metrics.pairwise import cosine_similarity
from app.processing.cleaner import clean

db_path = r"c:\Users\Vaibhav\Desktop\test-2\data\processed\prod.sqlite"

def get_leads_simulation_with_semantic(q=None):
    print(f"\n--- SIMULATING API CALL FOR q='{q}' (WITH SEMANTIC FALLBACK) ---")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    clean_q = clean(q) if q else None
    
    query = "SELECT * FROM leads WHERE 1=1"
    params = []
    if clean_q:
        query += " AND clean_comment LIKE ?"
        params.append(f"%{clean_q}%")
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    result = []
    for r in rows:
        reason = r["reason"]
        if q and ("demo" in reason or not reason):
            reason = f"Matched search query '{q}' with relevance."
        result.append({"post_id": r["post_id"], "reason": reason, "match_type": "exact"})
    
    # SEMANTIC FALLBACK (Phase 10 logic in routes.py)
    if q and len(result) == 0:
        print("[DEBUG] No exact match, trying Semantic...")
        cursor.execute("SELECT * FROM leads")
        all_rows = cursor.fetchall()
        if all_rows:
            model = get_embedding_model()
            q_emb = model.encode([clean_q])
            texts = [r['clean_comment'] or r['comment'] for r in all_rows]
            embs = model.encode(texts)
            sims = cosine_similarity(q_emb, embs)[0]
            
            for idx, sim in enumerate(sims):
                if sim > 0.3:
                    r = all_rows[idx]
                    result.append({"post_id": r["post_id"], "reason": r["reason"], "match_type": "semantic", "score": float(sim)})
            
            result.sort(key=lambda x: x.get("score", 0), reverse=True)
            result = result[:10]

    if not result:
        print(f"RESULT: No leads found matching your query '{q}'.")
    else:
        print(f"RESULT: Found {len(result)} leads.")
        for res in result:
            print(f"  - Lead ID: {res['post_id']} | Type: {res['match_type']} | Reason: {res['reason']}")
            
    conn.close()

# TEST CASE for unexpected keyword
get_leads_simulation_with_semantic("doctor")
get_leads_simulation_with_semantic("nothingrelevant")
