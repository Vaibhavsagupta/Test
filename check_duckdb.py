import duckdb
import os

db_path = r"c:\Users\Vaibhav\Desktop\test-2\data\processed\local.duckdb"
if os.path.exists(db_path):
    con = duckdb.connect(db_path)
    try:
        print(con.execute("DESCRIBE candidates").df())
    except Exception as e:
        print(f"Error: {e}")
    con.close()
else:
    print("local.duckdb does not exist yet.")
