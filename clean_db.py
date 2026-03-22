import sqlite3
import os

db_path = r"c:\Users\Vaibhav\Desktop\test-2\data\processed\prod.sqlite"
conn = sqlite3.connect(db_path)
conn.execute("DELETE FROM leads WHERE post_id LIKE 'demo%'")
conn.commit()
print("Deleted dummy leads.")
count = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
print(f"Total real leads in DB now: {count}")
conn.close()
