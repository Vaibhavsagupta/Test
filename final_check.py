import sqlite3
import os

db_path = r"c:\Users\Vaibhav\Desktop\test-2\data\processed\prod.sqlite"
conn = sqlite3.connect(db_path)
count = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
print(f"Current Total Leads: {count}")

print("Leads by subreddit:")
rows = conn.execute("SELECT subreddit, COUNT(*) FROM leads GROUP BY subreddit").fetchall()
for r in rows:
    print(f"  - {r[0]}: {r[1]}")
conn.close()
