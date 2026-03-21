from app.services.reddit_client import RedditClient
from app.utils.text_cleaner import clean_text
from app.services.keyword_extractor import extract_keywords
from app.services.intent_detector import detect_intent
from app.services.lead_scorer import score_lead

client = RedditClient()

def extract_leads_pipeline(url):
    # Fetch data from Reddit
    data = client.get_data(url)
    post_info = data.get("post_info", {})
    
    # Check for NSFW
    from app.config import settings
    if post_info.get("over_18", False) and settings.ENABLE_NSFW_FILTERING:
        return {"error": "NSFW content is blocked by current safety settings.", "url": url}

    raw_comments = data.get("comments", [])

    results = []

    for item in raw_comments:
        comment_text = item.get("body", "")
        author = item.get("author", "N/A")
        
        # Pre-process
        clean = clean_text(comment_text)

        # Basic length (quality) filter
        if len(clean) < 15:
            continue

        # Task 2 logical flow
        keywords = extract_keywords(clean)
        sim_score = detect_intent(clean)
        score, label = score_lead(sim_score)

        # Filter out low leads for cleaner extraction
        if label == "LOW":
            continue

        results.append({
            "author": author,
            "comment": comment_text,
            "keywords": keywords,
            "lead_score": round(score, 3),
            "intent": label
        })

    return {
        "url": url,
        "post_context": post_info,
        "lead_count": len(results),
        "leads": sorted(results, key=lambda x: x['lead_score'], reverse=True)
    }
