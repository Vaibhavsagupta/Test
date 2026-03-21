import json
import os
from pathlib import Path
from app.config import settings

def get_tracker_path():
    path = settings.PROCESSED_DIR / "processed_files.json"
    if not path.exists():
        with open(path, 'w') as f:
            json.dump([], f)
    return path

def is_file_processed(file_name):
    path = get_tracker_path()
    with open(path, 'r') as f:
        processed_files = json.load(f)
    return file_name in processed_files

def mark_file_processed(file_name):
    path = get_tracker_path()
    with open(path, 'r') as f:
        processed_files = json.load(f)
    
    if file_name not in processed_files:
        processed_files.append(file_name)
        with open(path, 'w') as f:
            json.dump(processed_files, f, indent=2)
