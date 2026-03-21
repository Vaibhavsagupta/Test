from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
from app.config import settings


# Task 1 Reuse
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

def get_icp_embedding(client_name="hair_clinic"):
    try:
        with open(settings.CLIENTS_CONFIG_PATH, 'r') as f:
            clients = json.load(f)

    except FileNotFoundError:
        return None

    icp_keywords = clients.get(client_name, {}).get("icp", [])
    if not icp_keywords:
        return None

    icp_text = " ".join(icp_keywords)
    if model and icp_text:
        return model.encode([icp_text])[0]
    return None

def semantic_match(records, client_name="hair_clinic"):
    print(f"[SEMANTIC] Computing semantic scores for {len(records)} records...")
    
    if not model or not records:
        for r in records: r["semantic_score"] = 0.5
        return records

    icp_emb = get_icp_embedding(client_name)
    if icp_emb is None:
        for r in records: r["semantic_score"] = 0.5
        return records

    texts = [r.get("clean_comment", "") for r in records]
    embeddings = model.encode(texts)
    similarities = cosine_similarity(embeddings, [icp_emb])

    for i, r in enumerate(records):
        r["semantic_score"] = float(similarities[i][0])
    
    return records
