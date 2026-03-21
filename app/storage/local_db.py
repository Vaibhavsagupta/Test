import duckdb
from app.config import settings
import pandas as pd

def store_local(records):
    print(f"[LOCAL DB] Storing {len(records)} records to DuckDB Historical Index...")
    if not records:
        return
        
    con = duckdb.connect(str(settings.LOCAL_DB_PATH))
    df = pd.DataFrame(records)
    
    # Optional logic to manage schema changes simply create/insert
    try:
        con.execute("CREATE TABLE IF NOT EXISTS raw_leads AS SELECT * FROM df WHERE 1=0")
        con.execute("INSERT INTO raw_leads SELECT * FROM df")
    except Exception as e:
        print(f"[LOCAL DB ERROR] {e}")
        
    con.close()
