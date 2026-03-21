import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional
import time

app = FastAPI(title="Subreddit Recommendation Engine")

# Paths
MODELS_DIR = "models"
FEEDBACK_LOG = "data/feedback_logs.pkl"

# Global Models
print("Loading indices into memory...")
model = SentenceTransformer('all-MiniLM-L6-v2')
index = faiss.read_index(os.path.join(MODELS_DIR, "subreddit_faiss.index"))
with open(os.path.join(MODELS_DIR, "bm25_model.pkl"), 'rb') as f:
    bm25 = pickle.load(f)
with open(os.path.join(MODELS_DIR, "subreddit_mapping.pkl"), 'rb') as f:
    mapping = pickle.load(f) # list of {subreddit, description, subscribers}
with open(os.path.join(MODELS_DIR, "relation_graph.pkl"), 'rb') as f:
    graph = pickle.load(f)

# Initialize feedback storage
if os.path.exists(FEEDBACK_LOG):
    with open(FEEDBACK_LOG, 'rb') as f:
        feedback_data = pickle.load(f)
else:
    feedback_data = {} # (query, subreddit) -> score_boost

class FeedbackRequest(BaseModel):
    query: str
    subreddit: str
    action: str

@app.get("/search")
def search(q: str, top_k: int = 10):
    start_time = time.time()
    
    # 1. Semantic Search (Top 50)
    query_vector = model.encode([q], normalize_embeddings=True).astype('float32')
    scores, indices = index.search(query_vector, 50)
    
    candidates = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < len(mapping):
            res = mapping[idx].copy()
            res['semantic_score'] = float(score)
            res['index'] = int(idx)
            res['subscribers'] = int(res.get('subscribers', 0))
            candidates.append(res)
            
    # 2. BM25 Re-ranking
    tokenized_query = q.lower().split()
    all_bm25_scores = bm25.get_scores(tokenized_query)
    
    candidate_bm25_scores = [all_bm25_scores[c['index']] for c in candidates]
    # Normalize BM25
    if len(candidate_bm25_scores) > 0 and max(candidate_bm25_scores) > 0:
        max_bm25 = max(candidate_bm25_scores)
        candidate_bm25_scores = [s / max_bm25 for s in candidate_bm25_scores]
    
    for i, c in enumerate(candidates):
        c['keyword_score'] = float(candidate_bm25_scores[i])
        
    # 3. Engagement Score (Normalized Subscribers)
    max_subs = max([c['subscribers'] for c in mapping]) if mapping else 1
    for c in candidates:
        c['engagement_score'] = float(np.log1p(c['subscribers']) / np.log1p(max_subs))
        
    # 4. Relation Score
    candidate_names = set([c['subreddit'].lower() for c in candidates])
    for c in candidates:
        name = c['subreddit'].lower()
        related = graph.get(name, [])
        # Count how many related subreddits are in the top candidates
        shared = len(set(related).intersection(candidate_names))
        c['relation_score'] = min(1.0, shared / 5.0) # Cap at 5 relations
        
    # 5. Feedback Boost
    for c in candidates:
        key = (q.lower(), c['subreddit'].lower())
        c['feedback_score'] = float(feedback_data.get(key, 0.0))
        
    # Final Hybrid Score
    # 0.50 * semantic + 0.20 * keyword + 0.15 * engagement + 0.10 * relation + 0.05 * feedback
    for c in candidates:
        c['final_score'] = float(
            0.50 * c['semantic_score'] +
            0.20 * c['keyword_score'] +
            0.15 * c['engagement_score'] +
            0.10 * c['relation_score'] +
            0.05 * c['feedback_score']
        )
        
    # Sort and return top_k
    candidates.sort(key=lambda x: x['final_score'], reverse=True)
    results = candidates[:top_k]
    
    return {
        "query": q,
        "top_k": top_k,
        "results": results,
        "latency_ms": round((time.time() - start_time) * 1000, 2)
    }

@app.post("/feedback")
def log_feedback(req: FeedbackRequest):
    key = (req.query.lower(), req.subreddit.lower())
    # Simple CTR-style boost: increment by 0.1 each click, max 1.0
    feedback_data[key] = min(1.0, feedback_data.get(key, 0.0) + 0.1)
    
    with open(FEEDBACK_LOG, 'wb') as f:
        pickle.dump(feedback_data, f)
        
    return {"status": "success", "subreddit": req.subreddit}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
