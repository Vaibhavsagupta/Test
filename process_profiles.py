import pandas as pd
import re
import os

# Paths
RAW_DIR = "data/raw"
INTERIM_DIR = "data/interim"
PROCESSED_DIR = "data/processed"

def extract_subreddit(url):
    try:
        match = re.search(r'/r/([^/]+)/', str(url))
        if match:
            return match.group(1).lower()
    except:
        pass
    return None

def clean():
    print("Starting Phase 4: Cleaning & Normalization...")
    
    # 1. Load Metadata
    meta_df = pd.read_csv(os.path.join(RAW_DIR, "subreddits_metadata.csv"), engine='python', on_bad_lines='skip')
    
    # Filter out NSFW (Not Safe For Work) subreddits
    if 'over18' in meta_df.columns:
        # Convert to boolean-like check
        meta_df = meta_df[~meta_df['over18'].astype(str).str.lower().isin(['true', '1', 't', 'yes'])]
    
    # Additional Keyword Filter (Final Safeguard)
    nsfw_keywords = ['nsfw', 'porn', 'sex', 'gonewild', 'adult', 'erotica']
    if 'subreddit_name' in meta_df.columns:
        pattern = '|'.join(nsfw_keywords)
        meta_df = meta_df[~meta_df['subreddit_name'].str.contains(pattern, case=False, na=False)]
        
    meta_df = meta_df[['subreddit_name', 'public_description', 'subscribers_count']].copy()
    meta_df.columns = ['subreddit', 'description', 'subscribers']
    meta_df['subreddit'] = meta_df['subreddit'].str.lower()
    meta_df = meta_df.drop_duplicates('subreddit').dropna(subset=['subreddit'])
    
    # 2. Load Posts & Extract Subreddit
    posts_df = pd.read_csv(os.path.join(RAW_DIR, "pushshift_sample.csv"), engine='python', on_bad_lines='skip')
    posts_df['subreddit'] = posts_df['url'].apply(extract_subreddit)
    posts_df = posts_df.dropna(subset=['subreddit'])
    posts_df = posts_df[['subreddit', 'title']].copy()
    
    # Group posts by subreddit to get top N titles
    grouped_posts = posts_df.groupby('subreddit')['title'].apply(lambda x: " | ".join(list(x)[:10])).reset_index()
    grouped_posts.columns = ['subreddit', 'post_titles']
    
    # 3. Join Metadata and Posts
    merged_df = pd.merge(meta_df, grouped_posts, on='subreddit', how='left')
    merged_df['description'] = merged_df['description'].fillna("")
    merged_df['post_titles'] = merged_df['post_titles'].fillna("")
    
    # 4. Phase 5: Build Profile Text
    print("Starting Phase 5: Profile Construction...")
    def build_profile(row):
        parts = [str(row['subreddit']), str(row['description'])]
        if row['post_titles']:
            parts.append(f"Top posts: {row['post_titles']}")
        return " | ".join(parts).lower()

    merged_df['profile_text'] = merged_df.apply(build_profile, axis=1)
    
    # Save processed data
    merged_df.to_parquet(os.path.join(PROCESSED_DIR, "subreddit_profiles.parquet"), index=False)
    print(f"Processed {len(merged_df)} subreddit profiles.")

if __name__ == "__main__":
    clean()
