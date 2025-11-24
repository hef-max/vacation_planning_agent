from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Vacation Planner API"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str
    
    # LLM (Ollama)
    GOOGLE_API_KEY: str
    LLM_BASE_URL: str
    LLM_MODEL: str
    
    # Security
    REQUIRE_BOOKING_CONFIRMATION: bool = True
    MAX_BUDGET_IDR: int = 50_000_000
    
    class Config:
        pass
        # env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()