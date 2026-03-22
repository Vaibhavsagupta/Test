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
    
    # Calculate 12 months ago epoch
    twelve_months_ago = int((datetime.now() - timedelta(days=365)).timestamp())
    
    return subreddits, twelve_months_ago

def query_comments(file_path, client_name="hair_clinic", target_subreddit=None):
    print(f"[DUCKDB ENGINE] Querying Comments from {file_path} with Early Filtering...")
    
    subreddits, min_timestamp = get_client_filtering_params(client_name)
    if target_subreddit and target_subreddit.lower() not in [s.lower() for s in subreddits]:
        subreddits.append(target_subreddit)
    
    con = duckdb.connect()
    
    # Build Subreddit Filter
    sub_filter = ""
    if subreddits:
        subs_str = "', '".join([s.lower() for s in subreddits])
        sub_filter = f"AND LOWER(subreddit) IN ('{subs_str}')"
    
    query = f"""
        SELECT 
            CAST(id AS VARCHAR) as comment_id, 
            CAST(link_id AS VARCHAR) as post_id, 
            CAST(body AS VARCHAR) as comment, 
            CAST(subreddit AS VARCHAR) as subreddit, 
            CAST(score AS BIGINT) as score, 
            CAST(created_utc AS BIGINT) as created_utc 
        FROM read_json_auto('{file_path}') 
        WHERE created_utc >= {min_timestamp}
        AND body NOT IN ('[deleted]', '[removed]')
        AND score IS NOT NULL
        {sub_filter}
    """
    
    try:
        df = con.execute(query).df()
        
        # Phase 1: Save to Compact DB (local.duckdb)
        # Using a persistent connection for storage might be better if we want to build a historical index
        local_con = duckdb.connect(str(settings.LOCAL_DB_PATH))
        local_con.execute("DROP TABLE IF EXISTS candidates")
        local_con.execute("CREATE TABLE candidates AS SELECT * FROM df")
        local_con.close()
        
        print(f"[DUCKDB ENGINE] Found {len(df)} candidates from comments.")
        return df.to_dict(orient="records")
    except duckdb.Error as e:
        print(f"[DUCKDB ENGINE ERROR] Query failed: {e}")
        return []

def query_submissions(file_path, client_name="hair_clinic", target_subreddit=None):
    print(f"[DUCKDB ENGINE] Querying Submissions from {file_path} with Early Filtering...")
    
    subreddits, min_timestamp = get_client_filtering_params(client_name)
    if target_subreddit and target_subreddit.lower() not in [s.lower() for s in subreddits]:
        subreddits.append(target_subreddit)
    
    con = duckdb.connect()
    
    # Build Filter
    sub_filter = ""
    if subreddits:
        subs_str = "', '".join([s.lower() for s in subreddits])
        sub_filter = f"AND LOWER(subreddit) IN ('{subs_str}')"
    
    # Keyword filter for early pruning
    kw_filter = ""
    from app.config import settings
    with open(settings.CLIENTS_CONFIG_PATH, 'r') as f:
        config = json.load(f).get(client_name, {})
        kws = config.get("keywords", []) + config.get("icp", [])
        if kws:
            kw_clauses = [f"LOWER(selftext) LIKE '%{kw.lower()}%' OR LOWER(title) LIKE '%{kw.lower()}%'" for kw in kws]
            kw_filter = f"AND ({' OR '.join(kw_clauses)})"

    query = f"""
        SELECT 
            CAST(id AS VARCHAR) as comment_id, 
            CAST(id AS VARCHAR) as post_id, 
            CAST((title || ' ' || COALESCE(selftext, '')) AS VARCHAR) as comment, 
            CAST(subreddit AS VARCHAR) as subreddit, 
            CAST(score AS BIGINT) as score, 
            CAST(created_utc AS BIGINT) as created_utc 
        FROM read_json_auto('{file_path}') 
        WHERE created_utc >= {min_timestamp}
        AND (selftext NOT IN ('[deleted]', '[removed]') OR selftext IS NULL)
        AND score IS NOT NULL
        {sub_filter}
        {kw_filter}
    """
    
    try:
        df = con.execute(query).df()
        
        # Phase 1: Save to Compact DB (local.duckdb)
        local_con = duckdb.connect(str(settings.LOCAL_DB_PATH))
        local_con.execute("DROP TABLE IF EXISTS candidates")
        local_con.execute("CREATE TABLE candidates AS SELECT * FROM df")
        local_con.close()
        
        print(f"[DUCKDB ENGINE] Found {len(df)} candidates from submissions.")
        return df.to_dict(orient="records")
    except duckdb.Error as e:
        print(f"[DUCKDB ENGINE ERROR] Query failed: {e}")
        return []

