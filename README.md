# Subreddit & Lead Mining Engine

A high-performance system for subreddit recommendation and historical Reddit lead mining.

## How to Start the Server

### 1. Local Development (Windows/Linux)
To run the API server locally on your machine:

```bash
# Using Uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
The API will be available at `http://localhost:8000` and the interactive docs at `http://localhost:8000/docs`.

### 2. Production Deployment (Docker)
The system is ready for production using Docker and Docker Compose.

```bash
# Build and start the container in detached mode
docker-compose up --build -d

# To stop the server
docker-compose down
```

---

## Historical Data Mining (Offline ZST)
To process large `.zst` Reddit dumps and extract high-intent leads:

1. **Run Ingestion:**
   ```bash
   python ingest_bulk_zst.py
   ```
2. **Track Progress (Stats Dashboard):**
   ```bash
   python zst_stats.py
   ```

---

## Project Structure
- `app/main.py`: Main API entry point.
- `app/api/routes.py`: API endpoints for Search, Extraction, and Historical Leads.
- `ingest_bulk_zst.py`: Optimized offline miner (Zstd support).
- `zst_stats.py`: Dashboard for mining progress and stats.
- `app/config/clients.json`: Per-client keywords, ICP, and subreddits.
- `data/processed/prod.sqlite`: Production database for filtered leads.

## Key API Endpoints
- `GET /search?q=query`: Recommend subreddits.
- `GET /extract-leads?url=link`: Extract leads from a live Reddit post.
- `GET /historical-leads?client=name`: Retrieve mined leads from the database.

---
*Created by the Advanced Agentic Coding Team.*
