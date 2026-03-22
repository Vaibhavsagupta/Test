import sqlite3
import os
import json
from pathlib import Path
import time
from datetime import datetime

def show_dump_stats():
    DB_PATH = Path("data/processed/prod.sqlite")
    PROGRESS_FILE = Path(".ingest_progress.json")
    
    if not DB_PATH.exists():
        print("Waiting for database to initialize...")
        return

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("--- 📂 ZST DUMP PROCESSING DASHBOARD ---")
        
        # Read Progress File (if it exists)
        progress_data = None
        if PROGRESS_FILE.exists():
            try:
                with open(PROGRESS_FILE, 'r') as f:
                    progress_data = json.load(f)
            except:
                pass

        if progress_data:
            pct = progress_data["percent"]
            completed = progress_data["files_completed"]
            total = progress_data["total_files"]
            current = progress_data["current_file"]
            client = progress_data["current_client"]
            
            # Progress Bar
            bar_len = 40
            filled = int(bar_len * pct / 100)
            bar = "█" * filled + "-" * (bar_len - filled)
            
            print(f"📊 Overall Progress: [{bar}] {pct}%")
            print(f"📁 Tasks: {completed} / {total} Completed ({total - completed} Remaining)")
            print(f"⛏️  Current: {current} (Client: {client})")
            
            # ETA Calculation
            try:
                start_time = datetime.fromisoformat(progress_data["start_time"])
                elapsed = (datetime.now() - start_time).total_seconds()
                if completed > 0:
                    time_per_task = elapsed / completed
                    remaining_tasks = total - completed
                    eta_seconds = time_per_task * remaining_tasks
                    eta_min = int(eta_seconds // 60)
                    eta_sec = int(eta_seconds % 60)
                    print(f"⌛ Estimated Time Remaining: {eta_min}m {eta_sec}s")
                else:
                    print(f"⌛ Estimating time...")
            except:
                pass
        else:
            print("Status: Active/Searching for leads...")
        
        print("-" * 50)
        
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()
            
            query = "SELECT source_file, COUNT(*) FROM leads GROUP BY source_file ORDER BY COUNT(*) DESC"
            cursor.execute(query)
            rows = cursor.fetchall()
            
            total_historical = 0
            print(f"{'Source ZST File':<35} | {'Leads Found':<10}")
            print("-" * 50)
            
            for row in rows:
                source = row[0] or "legacy/api"
                count = row[1]
                total_historical += count
                # Shorten source for display
                print(f"{source[:34]:<35} | {count:<10}")
            
            print("-" * 50)
            print(f"TOTAL HISTORICAL LEADS: {total_historical}")
            
            # Show last 3 real leads
            print("\n--- 🆕 LATEST HISTORICAL LEADS ---")
            cursor.execute("SELECT subreddit, comment FROM leads ORDER BY id DESC LIMIT 3")
            latest = cursor.fetchall()
            for l in latest:
                print(f" ✅ [r/{l[0]}] {l[1][:80]}...")
            
            conn.close()
        except Exception as e:
            print(f"Scanning files... ({e})")
        
        print("\n(Refresh: 10s... Press Ctrl+C to exit)")
        time.sleep(10)

if __name__ == "__main__":
    show_dump_stats()
