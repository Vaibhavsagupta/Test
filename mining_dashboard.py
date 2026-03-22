import json
import sqlite3
import time
import os
from pathlib import Path

# Paths
PROCESS_DIR = Path(r"c:/Users/Vaibhav/Desktop/test-2/data/processed")
TRACKER_PATH = PROCESS_DIR / "processed_files.json"
DB_PATH = PROCESS_DIR / "prod.sqlite"

# Define All Planned Tasks (27 total)
TASKS = [
    "HairTransplants", "tressless", "hair transplant", "baldness", "hair loss", "receding hairline",
    "legaladvice", "LegalAdviceUK", "lawyer", "solicitor", "attorney", "legal help", "lawsuit", "court", "landlord tenant", "employment law", "legal advice needed",
    "Turkey", "travel", "Istanbul", "travel guide", "hotel recommendation", "itinerary", "visiting", "trip planning", "safe places to visit", "best restaurants"
]

def get_stats():
    # Get processed count
    processed_count = 0
    if TRACKER_PATH.exists():
        with open(TRACKER_PATH, 'r') as f:
            try:
                processed = json.load(f)
                # Count matches with TASKS
                processed_count = len([x for x in processed if any(t in x for t in TASKS)])
            except: pass

    # Get DB Lead count
    total_leads = 0
    if DB_PATH.exists():
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM leads")
            total_leads = cursor.fetchone()[0]
            conn.close()
        except: pass

    return processed_count, total_leads

print("--- 📡 LIVE MINING DASHBOARD ---")
print(f"Total Categories Planned: {len(TASKS)}")
print("-" * 35)

start_time = time.time()

while True:
    processed, leads = get_stats()
    percent = (processed / len(TASKS)) * 100 if len(TASKS) > 0 else 0
    
    # Estimate time remaining (if at least one task is finished)
    elapsed = time.time() - start_time
    if processed > 0:
        time_per_task = elapsed / processed
        remaining_tasks = len(TASKS) - processed
        eta_seconds = remaining_tasks * time_per_task
        eta_min = round(eta_seconds / 60, 1)
    else:
        eta_min = "Calculating..."

    os.system('cls' if os.name == 'nt' else 'clear')
    print("--- 📡 LIVE MINING DASHBOARD ---")
    print(f"Status: Global Mining for 12-Month Data")
    print("-" * 35)
    print(f"Total Categories: {len(TASKS)}")
    print(f"Tasks Completed:  {processed} / {len(TASKS)} ({round(percent, 1)}%)")
    print(f"Total Database Leads: {leads}")
    print(f"Estimated Time Left: {eta_min} minutes")
    print("-" * 35)
    print("Mined Categories so far:")
    if TRACKER_PATH.exists():
        with open(TRACKER_PATH, 'r') as f:
            try:
                processed_list = json.load(f)[-5:] # Show last 5
                for p in processed_list: print(f" ✅ {p}")
            except: pass
    
    print("\nNext category mining now...")
    print("(Press Ctrl+C to close dashboard, mining continues in background)")
    
    time.sleep(30)
