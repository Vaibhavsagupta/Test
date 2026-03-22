import sqlite3

db_path = r"c:\Users\Vaibhav\Desktop\test-2\data\processed\prod.sqlite"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

print("Checking for any leads containing 'demo' in reason or post_id:")
rows = conn.execute("SELECT post_id, reason, subreddit FROM leads WHERE post_id LIKE 'demo%' OR reason LIKE '%demo%'").fetchall()
if not rows:
    print("NO DEMO LEADS FOUND IN THE DB!")
else:
    for r in rows:
        print(f"ID: {r['post_id']} | Sub: {r['subreddit']} | Reason: {r['reason']}")

print("\nSample of newest leads (Real ones):")
real_rows = conn.execute("SELECT post_id, subreddit, reason FROM leads ORDER BY id DESC LIMIT 5").fetchall()
for r in real_rows:
    print(f"ID: {r['post_id']} | Sub: {r['subreddit']} | Reason: {r['reason']}")
conn.close()
