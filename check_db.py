import sqlite3
import re
from pathlib import Path

db_path = r"c:/Users/Vaibhav/Desktop/test-2/data/processed/prod.sqlite"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT id, comment FROM leads")
rows = cursor.fetchall()
hindi_count = 0
for row in rows:
    comment = row['comment']
    # Range for Devanagari (Hindi)
    if any('\u0900' <= c <= '\u097f' for c in comment):
        hindi_count += 1
        if hindi_count <= 3:
            print(f"ID: {row['id']} | HINDI: {comment[:50]}...")

print(f"Total rows with Hindi characters: {hindi_count} / {len(rows)}")
conn.close()





