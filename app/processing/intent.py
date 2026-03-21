def is_lead(text):
    triggers = ["looking", "suggest", "recommend", "cost", "best", "help", "clinic", "surgeon"]
    return any(t in text for t in triggers)

def intent_filter(records):
    print(f"[INTENT] Filtering {len(records)} records for intent...")
    filtered = []
    for r in records:
        text = r.get("clean_comment", "")
        if is_lead(text):
            r["intent"] = "HIGH"
            # Setting a base intent score, could be dynamic (0-1) later based on model
            r["intent_score"] = 0.8  
            filtered.append(r)
    
    print(f"[INTENT] Kept {len(filtered)} leads after intent matching.")
    return filtered
