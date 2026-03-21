
import requests

def test_search():
    url = "http://localhost:8000/search?q=porn"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"Results for '{data['query']}':")
            for res in data['results']:
                print(f"- {res['subreddit']}: {res['description'][:100]}...")
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    test_search()
