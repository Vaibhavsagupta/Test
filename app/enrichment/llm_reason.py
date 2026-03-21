import os
import json

# Placeholder for LLM Client (OpenAI/Gemini/Anthropic)
# To use a real one, set OPENAI_API_KEY env var and uncomment below:
# from openai import OpenAI
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_llm_reasoning(comment, subreddit):
    # This is a sophisticated prompt for Problem -> Solution mapping
    prompt = f"""
    Analyze the following Reddit comment from r/{subreddit}:
    "{comment}"
    
    Task:
    1. Identify the user's core problem.
    2. Suggest how a service/product could solve this.
    3. Output in format: "Problem: [problem] -> Solution: [solution]"
    
    Short reason ONLY (max 20 words).
    """
    
    # Mock return if no API key
    if not os.getenv("OPENAI_API_KEY"):
        # Improved rule-based reasoning as fallback
        c = comment.lower()
        if "clinic" in c or "surgeon" in c:
            return "Problem: Finding trustworthy medical help -> Solution: Verified clinic recommendation."
        if "cost" in c or "money" in c:
            return "Problem: Price sensitivity/budgeting -> Solution: Cost comparison & financing options."
        return "Problem: User seeking information/advice -> Solution: Targeted expert guidance."

    # In real production, you'd call the LLM here:
    # response = client.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=[{"role": "user", "content": prompt}]
    # )
    # return response.choices[0].message.content
    return "Problem: [Identified by AI] -> Solution: [Proposed by AI]"

def enrich_leads(records, top_n=50):
    print(f"[ENRICHMENT] LLM reasoning top {min(top_n, len(records))} leads...")
    
    results = []
    for r in records[:top_n]:
        comment = r.get("comment", "")
        subreddit = r.get("subreddit", "unknown")
        
        # Call the reasoning engine
        r["reason"] = get_llm_reasoning(comment, subreddit)
        
        # Preserve relationships and build permalink
        post_id = r.get("post_id", "").replace("t3_", "")
        comment_id = str(r.get("comment_id", ""))
        r["permalink"] = f"https://reddit.com/r/{subreddit}/comments/{post_id}/_/{comment_id}/"
        
        results.append(r)
        
    return results

