def score_lead(similarity_score):
    # Reduced thresholds for better demo visibility
    if similarity_score > 0.35:  # Was 0.5
        return similarity_score, "HIGH"
    elif similarity_score > 0.20: # Was 0.3
        return similarity_score, "MEDIUM"
    else:
        return similarity_score, "LOW"
