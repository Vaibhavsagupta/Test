import sqlite3
from app.config import settings

def store_prod(records):
    print(f"[PROD DB] Storing {len(records)} enriched leads to SQLite Production DB...")
    if not records:
        return
        
    conn = sqlite3.connect(str(settings.PROD_DB_PATH))

    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id TEXT,
        comment TEXT,
        subreddit TEXT,
        score INTEGER,
        intent TEXT,
        final_score REAL,
        reason TEXT,
        permalink TEXT,
        created_utc INTEGER
    )
    ''')
    
    for r in records:
        cursor.execute('''
        INSERT INTO leads (post_id, comment, subreddit, score, intent, final_score, reason, permalink, created_utc)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            r.get("post_id", ""),
            r.get("comment", ""),
            r.get("subreddit", ""),
            r.get("score", 0),
            r.get("intent", ""),
            r.get("final_score", 0.0),
            r.get("reason", ""),
            r.get("permalink", ""),
            r.get("created_utc", 0)
        ))

        
    conn.commit()
    conn.close()

