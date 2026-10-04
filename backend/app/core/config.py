from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "development"
    DATABASE_URL: str = "sqlite:///./app.db"
    
    PRIMARY_LLM_PROVIDER: str = "groq"
    PRIMARY_LLM_MODEL: str = "qwen/qwen3.8-27b"
    PRIMARY_LLM_API_KEY: str = ""
    
    FALLBACK_LLM_PROVIDER: str = "nvidia"
    FALLBACK_LLM_MODEL: str = "deepseek-ai/deepseek-v4.1-flash"
    FALLBACK_LLM_API_KEY: str = ""
    MAX_ITERATIONS: int = 5
    EXECUTION_TIMEOUT: int = 30
    
    class Config:
        env_file = "../.env"

settings = Settings()
