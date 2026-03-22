from sklearn.metrics.pairwise import cosine_similarity
from app.models.embedding_model import get_embedding_model

# Reused singleton model to save memory on 2GB RAM server
try:
    model = get_embedding_model()
except Exception:
    model = None

def deduplicate(records, threshold=0.9):
    print(f"[DEDUPLICATOR] Deduplicating {len(records)} leads...")
    if not records or not model:
        return records

    # Use original order (which is sorted by score DESC)
    texts = [r.get("clean_comment", "") for r in records]
    embeddings = model.encode(texts)
    
    unique_leads = []
    seen_indices = set()
    
    for i in range(len(records)):
        if i in seen_indices:
            continue
            
        unique_leads.append(records[i])
        
        # Check against following records
        if i + 1 < len(records):
            sims = cosine_similarity([embeddings[i]], embeddings[i+1:])[0]
            for j, sim in enumerate(sims):
                if sim > threshold:
                    seen_indices.add(i + 1 + j)
                    
    print(f"[DEDUPLICATOR] {len(unique_leads)} unique leads retained.")
    return unique_leads
