import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import time
from rank_bm25 import BM25Okapi

def test_search(q, top_k=5):
    # Paths
    MODELS_DIR = "models"
    
    # Load
    print(f"Testing search for: {q}")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    index = faiss.read_index(os.path.join(MODELS_DIR, "subreddit_faiss.index"))
    with open(os.path.join(MODELS_DIR, "bm25_model.pkl"), 'rb') as f:
        bm25 = pickle.load(f)
    with open(os.path.join(MODELS_DIR, "subreddit_mapping.pkl"), 'rb') as f:
        mapping = pickle.load(f)
    with open(os.path.join(MODELS_DIR, "relation_graph.pkl"), 'rb') as f:
        graph = pickle.load(f)

    # Search
    query_vector = model.encode([q], normalize_embeddings=True).astype('float32')
    scores, indices = index.search(query_vector, 50)
    
    candidates = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < len(mapping):
            res = mapping[idx].copy()
            res['semantic_score'] = float(score)
            res['index'] = idx
            candidates.append(res)
            
    # BM25
    tokenized_query = q.lower().split()
    all_bm25_scores = bm25.get_scores(tokenized_query)
    candidate_bm25_scores = [all_bm25_scores[c['index']] for c in candidates]
    if len(candidate_bm25_scores) > 0 and max(candidate_bm25_scores) > 0:
        max_bm25 = max(candidate_bm25_scores)
        candidate_bm25_scores = [s / max_bm25 for s in candidate_bm25_scores]
    
    for i, c in enumerate(candidates):
        c['keyword_score'] = float(candidate_bm25_scores[i])
        
    # Final Rank
    for c in candidates:
        # Simple hybrid for test
        c['final_score'] = 0.7 * c['semantic_score'] + 0.3 * c['keyword_score']
        
    candidates.sort(key=lambda x: x['final_score'], reverse=True)
    return candidates[:top_k]

if __name__ == "__main__":
    for query in ["Machine Learning", "Python Beginners"]:
        results = test_search(query)
        print(f"\nResults for '{query}':")
        for r in results:
            print(f"- {r['subreddit']}: {r['final_score']:.3f} | {r['description'][:60]}...")
