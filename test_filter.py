import sqlite3
import os

db_path = r"c:\Users\Vaibhav\Desktop\test-2\data\processed\prod.sqlite"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

def test_query(q):
    print(f"\n--- Testing query: '{q}' ---")
    query = "SELECT * FROM leads WHERE 1=1"
    params = []
    if q:
        query += " AND clean_comment LIKE ?"
        params.append(f"%{q}%")
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    print(f"Found {len(rows)} results")
    for r in rows:
        print(f"ID: {r['post_id']} | Subreddit: {r['subreddit']} | Clean Comment: {r['clean_comment'][:30]}...")

test_query("biscuit")
test_query("hairtransplants")
test_query("randomxyz")

conn.close()
