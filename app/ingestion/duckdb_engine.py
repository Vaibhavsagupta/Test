import duckdb
import json
import time
from datetime import datetime, timedelta
from app.config import settings

def get_client_filtering_params(client_name):
    try:
        with open(settings.CLIENTS_CONFIG_PATH, 'r') as f:
            clients = json.load(f)
    except Exception:
        return [], 0

    client_config = clients.get(client_name, {})
    subreddits = client_config.get("subreddits", [])
    
    # Calculate 6 months ago epoch
    six_months_ago = int((datetime.now() - timedelta(days=180)).timestamp())
    
    return subreddits, six_months_ago

def query_comments(file_path, client_name="hair_clinic"):
    print(f"[DUCKDB ENGINE] Querying Comments from {file_path} with Early Filtering...")
    
    subreddits, min_timestamp = get_client_filtering_params(client_name)
    
    con = duckdb.connect()
    
    # Build Subreddit Filter
    sub_filter = ""
    if subreddits:
        subs_str = "', '".join([s.lower() for s in subreddits])
        sub_filter = f"AND LOWER(subreddit) IN ('{subs_str}')"
    
    query = f"""
        SELECT 
            id as comment_id, 
            link_id as post_id, 
            body as comment, 
            subreddit, 
            score, 
            created_utc 
        FROM read_json_auto('{file_path}') 
        WHERE created_utc >= {min_timestamp}
        AND body NOT IN ('[deleted]', '[removed]')
        AND score > 0
        {sub_filter}
    """
    
    try:
        df = con.execute(query).df()
        
        # Phase 1: Save to Compact DB (local.duckdb)
        # Using a persistent connection for storage might be better if we want to build a historical index
        local_con = duckdb.connect(str(settings.LOCAL_DB_PATH))
        local_con.execute("CREATE TABLE IF NOT EXISTS candidates AS SELECT * FROM df WHERE 1=0")
        local_con.execute("INSERT INTO candidates SELECT * FROM df")
        local_con.close()
        
        print(f"[DUCKDB ENGINE] Found {len(df)} candidates from comments.")
        return df.to_dict(orient="records")
    except duckdb.Error as e:
        print(f"[DUCKDB ENGINE ERROR] Query failed: {e}")
        return []

def query_submissions(file_path, client_name="hair_clinic"):
    print(f"[DUCKDB ENGINE] Querying Submissions from {file_path} with Early Filtering...")
    
    subreddits, min_timestamp = get_client_filtering_params(client_name)
    
    con = duckdb.connect()
    
    # Build Subreddit Filter
    sub_filter = ""
    if subreddits:
        subs_str = "', '".join([s.lower() for s in subreddits])
        sub_filter = f"AND LOWER(subreddit) IN ('{subs_str}')"
    
    query = f"""
        SELECT 
            id as comment_id, 
            id as post_id, 
            (title || ' ' || COALESCE(selftext, '')) as comment, 
            subreddit, 
            score, 
            created_utc 
        FROM read_json_auto('{file_path}') 
        WHERE created_utc >= {min_timestamp}
        AND (selftext NOT IN ('[deleted]', '[removed]') OR selftext IS NULL)
        AND score > 0
        {sub_filter}
    """
    
    try:
        df = con.execute(query).df()
        
        # Phase 1: Save to Compact DB (local.duckdb)
        local_con = duckdb.connect(str(settings.LOCAL_DB_PATH))
        local_con.execute("CREATE TABLE IF NOT EXISTS candidates AS SELECT * FROM df WHERE 1=0")
        local_con.execute("INSERT INTO candidates SELECT * FROM df")
        local_con.close()
        
        print(f"[DUCKDB ENGINE] Found {len(df)} candidates from submissions.")
        return df.to_dict(orient="records")
    except duckdb.Error as e:
        print(f"[DUCKDB ENGINE ERROR] Query failed: {e}")
        return []

