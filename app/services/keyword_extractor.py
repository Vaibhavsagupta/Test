from keybert import KeyBERT

# Initialize outside of function if needed to be persistent, 
# although within this architecture, it is fine here.
kw_model = KeyBERT()

def extract_keywords(text):
    if not text:
        return []
    kws = kw_model.extract_keywords(text, top_n=3)
    return [k[0] for k in kws]
