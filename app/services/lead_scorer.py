def score_lead(similarity_score):
    if similarity_score > 0.7:
        return similarity_score, "HIGH"
    elif similarity_score > 0.4:
        return similarity_score, "MEDIUM"
    else:
        return similarity_score, "LOW"
