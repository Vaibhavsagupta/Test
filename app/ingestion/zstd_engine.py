import duckdb
from pathlib import Path

def query_zst_dump(file_path, query=None, subreddit=None, limit=1000):
    """
    Directly query Arctic Shift / Pushshift .zst dumps using DuckDB.
    No full decompression required.
    Satisfies 'Ingestion Engine' requirement for Lead Gen Pipeline.
    """
    con = duckdb.connect()
    
    # DuckDB can read zst directly if the zstd extension is loaded (usually included)
    # Mapping fields from raw reddit dump to our schema
    
    filters = ["created_utc >= (epoch(now()) - 15778800)"] # 6 months only
    filters.append("body NOT IN ('[deleted]', '[removed]')")
    if subreddit:
        filters.append(f"LOWER(subreddit) = '{subreddit.lower()}'")
    if query:
        filters.append(f"LOWER(body) LIKE '%{query.lower()}%'")
        
    where_clause = " AND ".join(filters)
    
    sql = f"""
        SELECT 
            id as comment_id, 
            link_id as post_id, 
            body as comment, 
            subreddit, 
            score, 
            created_utc 
        FROM read_json_auto('{file_path}', compression='zstd') 
        WHERE {where_clause}
        LIMIT {limit}
    """
    
    print(f"[ZSTD ENGINE] Querying local dump: {file_path}")
    try:
        df = con.execute(sql).df()
        return df.to_dict(orient="records")
    except Exception as e:
        print(f"[ZSTD ENGINE ERROR] {e}")
        return []
