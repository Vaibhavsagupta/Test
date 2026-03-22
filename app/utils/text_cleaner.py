import re

def clean_text(text):
    if not text:
        return ""
    text = text.lower()
    # Remove URLs
    text = re.sub(r"http\S+", "", text)
    # Remove punctuation but KEEP everything else (\w matches English/Hindi/etc. letters)
    text = re.sub(r"[^\w\s]", " ", text)
    # Strip whitespaces
    text = " ".join(text.split())
    return text

