import os
import pickle
import numpy as np
from app.models.embedding_model import EmbeddingModel
from app.models.faiss_index import FaissIndex

class RecommenderService:
    def __init__(self):
        self.model = EmbeddingModel()
        self.faiss_index = FaissIndex()
        
        # Paths for additional Task 1 files
        MODELS_DIR = os.path.join(os.path.dirname(__file__), "../../models")
        self.bm25_path = os.path.join(MODELS_DIR, "bm25_model.pkl")
        self.graph_path = os.path.join(MODELS_DIR, "relation_graph.pkl")
        
        if os.path.exists(self.bm25_path):
            with open(self.bm25_path, 'rb') as f:
                self.bm25 = pickle.load(f)
        else:
            self.bm25 = None
            
        if os.path.exists(self.graph_path):
            with open(self.graph_path, 'rb') as f:
                self.graph = pickle.load(f)
        else:
            self.graph = {}

    def search_subreddits(self, q, top_k=10):
        # 1. Semantic Search
        query_vector = self.model.encode([q]).detach().cpu().numpy().astype('float32')
        scores, indices = self.faiss_index.search(query_vector, 50)
        
        candidates = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.faiss_index.mapping):
                res = self.faiss_index.mapping[idx].copy()
                res['semantic_score'] = float(score)
                res['index'] = int(idx)
                res['subscribers'] = int(res.get('subscribers', 0))
                candidates.append(res)
        
        # 2. Hybrid Scoring logic could go here (omitted for brevity in Task 2 integration demo)
        # But we could reuse Task 1 logic if needed.
        
        return candidates[:top_k]
