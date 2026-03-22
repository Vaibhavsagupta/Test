from sentence_transformers import SentenceTransformer

# Singleton to save memory on server (2GB RAM limit)
_shared_model = None

def get_embedding_model():
    global _shared_model
    if _shared_model is None:
        _shared_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _shared_model

class EmbeddingModel:
    def __init__(self):
        self.model = get_embedding_model()

    def encode(self, texts, **kwargs):
        return self.model.encode(texts, convert_to_tensor=True, **kwargs)
