import sqlite3
import os

db_path = r"c:\Users\Vaibhav\Desktop\test-2\data\processed\prod.sqlite"

def get_leads_simulation(q=None):
    print(f"\n--- SIMULATING API CALL FOR q='{q}' ---")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # PHASE 6 Debug
    cursor.execute("SELECT COUNT(*) FROM leads")
    db_count = cursor.fetchone()[0]
    print(f"DEBUG: TOTAL DB ROWS: {db_count}")
    if q:
        print(f"DEBUG: USER QUERY: {q}")
    
    query = "SELECT * FROM leads WHERE 1=1"
    params = []
    if q:
        query += " AND clean_comment LIKE ?"
        params.append(f"%{q}%")
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    result = []
    for r in rows:
        # PHASE 6 loop debug
        print(f"DEBUG: CHECKING DB ROW: {r['clean_comment'][:50]}...")
        
        # PHASE 5: Dynamic reason
        reason = r["reason"]
        if q and ("demo" in reason or not reason or not reason.strip()):
            reason = f"Matched search query '{q}' with relevance."
        
        result.append({
            "post_id": r["post_id"],
            "reason": reason,
            "clean_comment": r["clean_comment"][:30]
        })
    
    if not result:
        print(f"FALLBACK: No leads found matching your query '{q}' or parameters.")
    else:
        print(f"SUCCESS: Found {len(result)} leads.")
        for res in result:
            print(f"  - Lead ID: {res['post_id']} | Reason: {res['reason']}")
            
    conn.close()

# TEST CASES (PHASE 7)
get_leads_simulation("biscuit")
get_leads_simulation("hairtransplants")
get_leads_simulation("randomxyz")
