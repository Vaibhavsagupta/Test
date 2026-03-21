import os
import faiss
import pickle

MODELS_DIR = os.path.join(os.path.dirname(__file__), "../../models")

class FaissIndex:
    def __init__(self):
        self.index_path = os.path.join(MODELS_DIR, "subreddit_faiss.index")
        self.mapping_path = os.path.join(MODELS_DIR, "subreddit_mapping.pkl")
        
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
        else:
            self.index = None
            
        if os.path.exists(self.mapping_path):
            with open(self.mapping_path, 'rb') as f:
                self.mapping = pickle.load(f)
        else:
            self.mapping = []

    def search(self, query_vector, top_k=50):
        if self.index is None:
            return [], []
        scores, indices = self.index.search(query_vector, top_k)
        return scores, indices
