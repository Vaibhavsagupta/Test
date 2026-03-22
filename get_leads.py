import sqlite3
from pathlib import Path

db_path = r"c:/Users/Vaibhav/Desktop/test-2/data/processed/prod.sqlite"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get top 10 leads by final score
cursor.execute("SELECT post_id, subreddit, comment, intent, final_score, reason FROM leads ORDER BY final_score DESC LIMIT 10")
rows = cursor.fetchall()

print("| Post ID | Subreddit | Intent | Score | Reason | Comment |")
print("|---|---|---|---|---|---|")
for row in rows:
    comment = row['comment'].replace('\n', ' ')[:50] + "..."
    reason = (row['reason'] or "").replace('\n', ' ')[:50] + "..."
    print(f"| {row['post_id']} | {row['subreddit']} | {row['intent']} | {round(row['final_score'], 3)} | {reason} | {comment} |")

conn.close()
