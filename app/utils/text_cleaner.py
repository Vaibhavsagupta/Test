import re

def clean_text(text):
    if not text:
        return ""
    text = text.lower()
    # Remove URLs
    text = re.sub(r"http\S+", "", text)
    # Remove special characters but keep spaces
    text = re.sub(r"[^a-zA-Z0-9 ]", "", text)
    # Strip leading/trailing whitespaces
    text = text.strip()
    return text
