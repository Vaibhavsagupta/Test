import sqlite3
import os

db_path = r"c:\Users\Vaibhav\Desktop\test-2\data\processed\prod.sqlite"
conn = sqlite3.connect(db_path)
schema = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='leads';").fetchone()[0]
print(schema)
conn.close()
