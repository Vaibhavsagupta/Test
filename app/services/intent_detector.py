from app.models.embedding_model import EmbeddingModel
from sentence_transformers import util

model = EmbeddingModel()

templates = [
    "I want to buy",
    "I am planning to get",
    "Looking for service",
    "Can someone suggest",
    "looking for the best clinic",
    "which surgeon is best",
    "how much does a hair transplant cost",
    "any advice for hair loss",
    "best place for treatment",
    "recommendations for surgery",
    "worth it to get a transplant",
    "budget friendly clinics",
    "before and after results",
    "help with receding hairline"
]

template_embeddings = model.encode(templates)

def detect_intent(comment):
    if not comment:
        return 0.0
    emb = model.encode([comment])
    # Semantic similarity using Task 1 model
    scores = util.cos_sim(emb, template_embeddings)
    return float(scores[0].max())
