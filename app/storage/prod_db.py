import sqlite3
from app.config import settings

def store_prod(records, client_name="unknown"):
    print(f"[PROD DB] Storing {len(records)} enriched leads for {client_name} to SQLite Production DB...")
    if not records:
        return
        
    conn = sqlite3.connect(str(settings.PROD_DB_PATH))
    cursor = conn.cursor()
    
    # Updated table schema with client_name
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id TEXT,
        comment TEXT,
        clean_comment TEXT,
        subreddit TEXT,
        score INTEGER,
        intent TEXT,
        final_score REAL,
        reason TEXT,
        permalink TEXT,
        created_utc INTEGER,
        source_file TEXT,
        client_name TEXT
    )
    ''')
    
    # Metadata table for incremental runs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS processed_files (
        filename TEXT PRIMARY KEY,
        processed_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    for r in records:
        cursor.execute('''
        INSERT INTO leads (post_id, comment, clean_comment, subreddit, score, intent, final_score, reason, permalink, created_utc, source_file, client_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            r.get("post_id", ""),
            r.get("comment", ""),
            r.get("clean_comment", ""),
            r.get("subreddit", ""),
            r.get("score", 0),
            r.get("intent", ""),
            r.get("final_score", 0.0),
            r.get("reason", ""),
            r.get("permalink", ""),
            r.get("created_utc", 0),
            r.get("source_file", "unknown"),
            client_name
        ))
        
    conn.commit()
    conn.close()

def log_file_processed(filename):
    conn = sqlite3.connect(str(settings.PROD_DB_PATH))
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO processed_files (filename) VALUES (?)", (filename,))
    conn.commit()
    conn.close()

def is_file_processed(filename):
    if not settings.PROD_DB_PATH.exists():
        return False
    conn = sqlite3.connect(str(settings.PROD_DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM processed_files WHERE filename = ?", (filename,))
    result = cursor.fetchone()
    conn.close()
    return result is not None
