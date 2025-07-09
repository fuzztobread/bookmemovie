import os
import sys
from pathlib import Path

class Config:
    def __init__(self):
        self._load_env_file()
        
        # Required from .env
        self.secret_key = self._get_required("SECRET_KEY")
        self.admin_email = self._get_required("ADMIN_EMAIL")
        self.admin_password = self._get_required("ADMIN_PASSWORD")
        
        # Optional from .env
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./movie_ticketing.db")
        self.debug = os.getenv("DEBUG", "true").lower() == "true"
        
        # Hardcoded constants
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.admin_name = "System Administrator"
        self.app_name = "Movie Ticketing API"
        self.app_version = "1.0.0"
        self.seat_lock_duration_minutes = 10
    
    def _load_env_file(self):
        try:
            from dotenv import load_dotenv
            env_path = Path(__file__).parent / ".env"
            if env_path.exists():
                load_dotenv(env_path)
        except ImportError:
            pass
    
    def _get_required(self, key: str) -> str:
        value = os.getenv(key)
        if not value:
            print(f"❌ Missing required environment variable: {key}")
            sys.exit(1)
        return value

# Singleton
_config = None

def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config()
    return _config
