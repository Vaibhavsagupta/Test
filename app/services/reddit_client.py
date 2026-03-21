import requests
from app.config import settings

class RedditClient:
    def __init__(self):
        # Even without PRAW, we need a good User-Agent
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }

    def get_data(self, url):
        """
        Option A: Fetches post/subreddit data via public .json endpoint.
        Returns a dictionary with 'post_info' and 'comments'.
        """
        try:
            # Clean URL: Add .json if not present
            if not url.endswith(".json"):
                # Handle potential trailing slash
                url = url.rstrip("/") + ".json"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            
            post_info = {}
            comments_list = []
            
            if isinstance(data, list) and len(data) > 0:
                # Post structure: [post_data, comment_data]
                post_data = data[0].get('data', {}).get('children', [{}])[0].get('data', {})
                post_info = {
                    "title": post_data.get('title'),
                    "subreddit": post_data.get('subreddit'),
                    "author": post_data.get('author'),
                    "selftext": post_data.get('selftext')
                }
                
                if len(data) > 1:
                    comments_list = data[1].get('data', {}).get('children', [])
            elif isinstance(data, dict):
                # Subreddit/Listing structure
                comments_list = data.get('data', {}).get('children', [])
            
            comments = []
            for c in comments_list:
                kind = c.get('kind', '')
                if kind == 't1': # t1 is the kind for comments
                    body = c.get('data', {}).get('body', "")
                    if body:
                        comments.append({
                            "body": body,
                            "author": c.get('data', {}).get('author')
                        })
                elif kind == 't3': # t3 is the kind for posts (if URL was a subreddit)
                    title = c.get('data', {}).get('title', "")
                    if title:
                        comments.append({
                            "body": f"POST: {title}\n{c.get('data', {}).get('selftext', '')}",
                            "author": c.get('data', {}).get('author')
                        })
            
            return {
                "post_info": post_info,
                "comments": comments
            }
            
        except Exception as e:
            print(f"Error fetching public data from {url}: {e}")
            return {"post_info": {}, "comments": []}

