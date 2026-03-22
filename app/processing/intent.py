from app.services.intent_detector import detect_intent

def intent_filter(records, threshold=0.10):
    print(f"[INTENT] AI filtering {len(records)} records for intent using Task 2 model...")
    filtered = []
    # Use Task 2's Embedding Similarity (AI Intent) in BATCh mode
    texts = [r.get("clean_comment", "") for r in records]
    
    from app.models.embedding_model import get_embedding_model
    from sentence_transformers import util
    import torch
    
    model = get_embedding_model()
    # Task 2 templates
    from app.services.intent_detector import templates
    template_embeddings = model.encode(templates, convert_to_tensor=True)
    
    # Encode all comments at once
    print(f"[INTENT] Encoding {len(texts)} comments for intent matching...")
    comment_embeddings = model.encode(texts, convert_to_tensor=True, show_progress_bar=True)
    
    # Calculate cosine similarity matrix
    sim_matrix = util.cos_sim(comment_embeddings, template_embeddings)
    # Get max similarity for each comment across templates
    max_scores = sim_matrix.max(dim=1).values
    
    for i, r in enumerate(records):
        intent_score = float(max_scores[i])
        if intent_score >= threshold:
            r["intent"] = "HIGH" if intent_score > 0.4 else "MED"
            r["intent_score"] = intent_score
            filtered.append(r)

    
    # Sort by intent score initially
    filtered.sort(key=lambda x: x["intent_score"], reverse=True)
    print(f"[INTENT] Kept {len(filtered)} real leads after AI matching.")
    return filtered
