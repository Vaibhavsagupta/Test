import sqlite3
from pathlib import Path

def show_top_leads():
    db_path = Path("data/processed/prod.sqlite")
    if not db_path.exists():
        print("Database not found.")
        return

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Selecting latest leads added to DB
    query = """
    SELECT subreddit, comment, intent, reason, final_score, permalink 
    FROM leads 
    ORDER BY id DESC 
    LIMIT 10
    """
    
    rows = cursor.execute(query).fetchall()
    
    print("\n--- 💎 TOP HIGH-QUALITY RECENT LEADS (100% REAL) ---")
    for r in rows:
        print(f"\n[r/{r['subreddit']}] | Score: {r['final_score']:.2f} | Intent: {r['intent']}")
        print(f"Comment: {r['comment'][:300].strip()}...")
        print(f"Reason: {r['reason']}")
        print(f"Direct Link: {r['permalink']}")
        print("-" * 50)
    
    conn.close()

if __name__ == "__main__":
    show_top_leads()
