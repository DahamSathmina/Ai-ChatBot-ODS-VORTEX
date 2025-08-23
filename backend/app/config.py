from pydantic import BaseSettings

class Settings(BaseSettings):
    # service
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Ollama
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma:2b"

    # Redis (sessions, rate limit)
    REDIS_URL: str = "redis://redis:6379/0"

    # Postgres (messages, users)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/ods"

    # FAISS embedding dim (depends on embedding model)
    EMBEDDING_DIM: int = 768

    # Security
    JWT_PUBLIC_KEY: str = ""   # use RS256 in prod
    JWT_ALGORITHM: str = "RS256"

    class Config:
        env_file = ".env"

settings = Settings()
