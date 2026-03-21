import os
# Fix for WinError 1114 / DLL initialization issues on Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Import torch first before other heavy DLL-using libraries like pandas/faiss
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import faiss
import pickle
from rank_bm25 import BM25Okapi

# Paths
PROCESSED_DIR = "data/processed"
MODELS_DIR = "models"

def build_indices():
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)

    print("Loading processed profiles...")
    df = pd.read_parquet(os.path.join(PROCESSED_DIR, "subreddit_profiles.parquet"))
    
    # 1. Phase 7: Semantic Embeddings
    print("Initializing embedding model (all-MiniLM-L6-v2) on CPU...")
    model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
    
    print(f"Encoding {len(df)} profiles (this may take a few minutes)...")
    embeddings = model.encode(df['profile_text'].tolist(), show_progress_bar=True, normalize_embeddings=True)
    
    # 2. Phase 8: FAISS Index
    print("Building FAISS index...")
    d = embeddings.shape[1]
    index = faiss.IndexFlatIP(d)  # Inner Product for Cosine Similarity since they are normalized
    index.add(embeddings.astype('float32'))
    
    faiss.write_index(index, os.path.join(MODELS_DIR, "subreddit_faiss.index"))
    
    # 3. Phase 9: Keyword Search (BM25)
    print("Building BM25 index...")
    tokenized_corpus = [text.split() for text in df['profile_text'].tolist()]
    bm25 = BM25Okapi(tokenized_corpus)
    
    with open(os.path.join(MODELS_DIR, "bm25_model.pkl"), 'wb') as f:
        pickle.dump(bm25, f)
        
    # Mapping
    mapping = df[['subreddit', 'description', 'subscribers']].to_dict('records')
    with open(os.path.join(MODELS_DIR, "subreddit_mapping.pkl"), 'wb') as f:
        pickle.dump(mapping, f)
        
    print("Index phase complete.")

if __name__ == "__main__":
    build_indices()
