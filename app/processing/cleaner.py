import re

def clean(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    # Remove URLs
    text = re.sub(r"http\S+", "", text)
    # Remove special punctuation but KEEP all letters (English, Hindi, etc.) and numbers
    # \w matches alphanumeric + underscores across languages in Python 3
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.split())

def clean_data(records):
    print(f"[CLEANER] Cleaning {len(records)} records...")
    for record in records:
        record["clean_comment"] = clean(record.get("comment", ""))
        
    # Return non-empty comments
    return [r for r in records if r["clean_comment"]]
