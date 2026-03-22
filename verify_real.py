import sqlite3
import os

db_path = r"c:\Users\Vaibhav\Desktop\test-2\data\processed\prod.sqlite"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

print("Querying r/HairTransplants leads:")
rows = conn.execute("SELECT post_id, subreddit, comment, reason FROM leads WHERE subreddit = 'HairTransplants' LIMIT 5").fetchall()
for r in rows:
    print(f"ID: {r['post_id']} | Reason: {r['reason'][:50]}... | Comment: {r['comment'][:50]}...")
conn.close()
