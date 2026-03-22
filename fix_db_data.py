import sqlite3
import re
from pathlib import Path

# The new inclusive cleaner logic
def clean(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.split())

db_path = r"c:/Users/Vaibhav/Desktop/test-2/data/processed/prod.sqlite"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get all rows
cursor.execute("SELECT id, comment FROM leads")
rows = cursor.fetchall()
print(f"Updating {len(rows)} leads with new cleaner...")

count = 0
for row in rows:
    new_clean = clean(row['comment'])
    cursor.execute("UPDATE leads SET clean_comment = ? WHERE id = ?", (new_clean, row['id']))
    count += 1

conn.commit()
print(f"✅ Updated {count} rows successfully.")
conn.close()
