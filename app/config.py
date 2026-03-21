import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Reddit Credentials (User to update these)
    REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID", "YOUR_ID")
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET", "YOUR_SECRET")
    REDDIT_USER_AGENT: str = os.getenv("REDDIT_USER_AGENT", "lead-extractor")

    # App Settings
    APP_TITLE: str = "Reddit Lead Recommendation System"
    
    class Config:
        env_file = ".env"

settings = Settings()
