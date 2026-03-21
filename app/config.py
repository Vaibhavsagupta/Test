import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Base Directories
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    RAW_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DIR: Path = DATA_DIR / "processed"
    
    # Task 3 Specific Paths
    CLIENTS_CONFIG_PATH: Path = BASE_DIR / "app" / "config" / "clients.json"
    LOCAL_DB_PATH: Path = PROCESSED_DIR / "local.duckdb"
    PROD_DB_PATH: Path = PROCESSED_DIR / "prod.sqlite"

    # Reddit Credentials (User to update these)
    REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID", "YOUR_ID")
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET", "YOUR_SECRET")
    REDDIT_USER_AGENT: str = os.getenv("REDDIT_USER_AGENT", "lead-extractor")

    # App Settings
    APP_TITLE: str = "Reddit Lead Recommendation System"
    
    # NSFW Filtering
    ENABLE_NSFW_FILTERING: bool = True
    NSFW_KEYWORDS: list = ["nsfw", "porn", "sex", "gonewild", "adult", "erotica", "hentai", "xxx"]
    
    class Config:
        env_file = ".env"

    def ensure_dirs(self):
        self.RAW_DIR.mkdir(parents=True, exist_ok=True)
        self.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.ensure_dirs()

