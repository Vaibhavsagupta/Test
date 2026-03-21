import pandas as pd
import pickle
import os
from collections import defaultdict

# Paths
RAW_DIR = "data/raw"
MODELS_DIR = "models"

def build_graph():
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)

    print("Loading SNAP relation links...")
    # Using small chunks to handle potentially large file if it were full
    links_path = os.path.join(RAW_DIR, "reddit_links.tsv")
    
    # Read only source/target
    try:
        df = pd.read_csv(links_path, sep='\t', usecols=['SOURCE_SUBREDDIT', 'TARGET_SUBREDDIT'])
        print(f"Loaded {len(df)} links.")
        
        # Build adjacency list
        graph = defaultdict(set)
        for _, row in df.iterrows():
            src = str(row['SOURCE_SUBREDDIT']).lower()
            tgt = str(row['TARGET_SUBREDDIT']).lower()
            graph[src].add(tgt)
            graph[tgt].add(src)  # Assuming bidirectional influence for recommendations
            
        # Convert set to list for pickling
        graph = {k: list(v) for k, v in graph.items()}
        
        with open(os.path.join(MODELS_DIR, "relation_graph.pkl"), 'wb') as f:
            pickle.dump(graph, f)
            
        print(f"Graph construction complete with {len(graph)} nodes.")
        
    except Exception as e:
        print(f"Error building graph: {e}")

if __name__ == "__main__":
    build_graph()
