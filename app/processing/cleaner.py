import re

def clean(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-zA-Z0-9 ]", "", text)
    return " ".join(text.split())

def clean_data(records):
    print(f"[CLEANER] Cleaning {len(records)} records...")
    for record in records:
        record["clean_comment"] = clean(record.get("comment", ""))
        
    # Return non-empty comments
    return [r for r in records if r["clean_comment"]]
