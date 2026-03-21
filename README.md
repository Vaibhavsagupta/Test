# Subreddit Recommendation Engine 🚀

A high-performance backend system that recommends subreddits based on user queries using a hybrid ranking algorithm. It combines semantic search, keyword matching, engagement metrics, and relational graph signals to provide accurate and diverse results.

---

## ✨ Features
- **Semantic Search**: Powered by `all-MiniLM-L6-v2` Sentence Transformers and `FAISS` for high-speed vector retrieval.
- **Keyword Matching**: BM25 algorithm for robust keyword-based re-ranking.
- **Hybrid Ranking**: Weighted scoring combining 5 distinct signals:
    - **Semantic (50%)**: Deep contextual understanding.
    - **Keyword (20%)**: Precise term matching.
    - **Engagement (15%)**: Normalized popularity/subscriber count.
    - **Relational (10%)**: Proximity in the Reddit hyperlink graph.
    - **Feedback (5%)**: Dynamic boost based on user interactions (clicks/engagement).
- **FastAPI Backend**: Asynchronous endpoints with low latency.
- **Data Pipeline**: Automated scripts for data acquisition, cleaning, and indexing.

---

## 🛠️ Technology Stack
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Vector Search**: [FAISS](https://github.com/facebookresearch/faiss)
- **NLP**: [Sentence-Transformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`)
- **Ranking**: `rank_bm25` (Okapi BM25)
- **Graph**: Reddit Hyperlinks adjacency list (SNAP Dataset)
- **Data Handling**: Pandas, NumPy, Parquet

---

## 📁 Project Structure
```text
test-2/
├── app.py              # Main FastAPI application & Hybrid Ranker
├── setup_datasets.py   # Phase 2: Downloads raw datasets (SNAP, GitHub, Kaggle)
├── process_profiles.py # Phase 4-5: Cleaning & Subreddit profile construction
├── build_indices.py    # Phase 7-9: FAISS index & BM25 model generation
├── build_graph.py      # Phase 10: Relational graph construction
├── data/               # Persistent data storage (raw, interim, processed)
├── models/             # Serialized models and indices (.pkl, .index, etc.)
└── test_ranker.py      # Standalone testing script for local validation
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- Virtual environment (recommended)

### 2. Setup & Installation
```powershell
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies (ensure these are installed)
pip install fastapi uvicorn sentence-transformers faiss-cpu rank_bm25 pandas numpy requests pyarrow
```

### 3. Run the Pipeline (Optional if models exist)
If you need to rebuild the indices from scratch:
```powershell
python setup_datasets.py  # Download data
python process_profiles.py # Clean and merge
python build_indices.py    # Create FAISS and BM25
python build_graph.py      # Create relational graph
```

### 4. Run the Engine
```powershell
python app.py
```
The server will be available at `http://localhost:8000`.

---

## 📡 API Endpoints

### `GET /search`
Find subreddits based on a natural language query.
- **Parameters**: 
  - `q` (string): The search query.
  - `top_k` (int, default=10): Number of results to return.
- **Example**: `GET /search?q=machine learning&top_k=5`

### `POST /feedback`
Submit user feedback to boost specific recommendations.
- **Body**:
```json
{
  "query": "machine learning",
  "subreddit": "MachineLearning",
  "action": "click"
}
```

### `GET /extract-leads` (Task 2: Lead Extraction)
Identify and score potential leads from a specific Reddit post URL.
- **Parameters**: 
  - `url` (string): The direct link to a Reddit post.
- **Functionality**:
  - Scrapes comments from the provided URL.
  - Automatically identifies user intent (High/Medium/Low interest).
  - Extracts key topics/keywords from each potential lead.
  - Assigns a numerical lead score for prioritization.
- **Example**: `GET /extract-leads?url=https://www.reddit.com/...`

### `GET /test-live`
A shortcut endpoint that tests the Task 2 pipeline with a pre-configured live Reddit post.

---

### `GET /health`
Verify server status.

---

## 💡 How It Works
1. **Retrieval**: FAISS retrieves the top 50 semantic candidates.
2. **Scoring**: Each candidate is scored for keywords (BM25), engagement (log-normalized subscribers), and relational popularity.
3. **Relation Graph**: Boosts subreddits that are frequently linked with other candidates in the result set.
4. **Final Sort**: Weighted sum of all scores determines the final order.
5. **Learning**: Clicks increase the `feedback_score` for specific query-subreddit pairs in future searches.

---
*Created by the Advanced Agentic Coding Team.*
