import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# Ensure directories exist
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

CLIENTS_CONFIG_PATH = BASE_DIR / "app" / "config" / "clients.json"
LOCAL_DB_PATH = PROCESSED_DIR / "local.duckdb"
PROD_DB_PATH = PROCESSED_DIR / "prod.sqlite"
