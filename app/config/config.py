from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    APP_NAME : str = "RAG-Observatory"
    API_V1_PREFIX : str  = "/api/v1"

    DEBUG : bool = False

    DATABASE_URL : str = "postgresql://postgres:postgres@postgres:5432/rag_db"
    REDIS_URL : str = "redis://redis:6379/0"
    CHROMA_HOST : str = "localhost"
    CHROMA_PORT : int = 8000
    CELERY_BROKER_URL : str = "redis://redis:6379/0"
    CELERY_BACKEND_URL : str = "redis://redis:6379/0"

    LOG_LEVEL : str = "INFO"

    OLLAMA_EMBED_MODEL : str = "nomic-embed-text" 
    OLLAMA_BASE_URL : str = "http://ollama:11434"
    OLLAMA_REWRITE_MODEL : str = "llama3"
    OLLAMA_GENERATION_MODEL : str = "llama3"

    GENERATION_MAX_TOKEN : int = 512
    GENERATION_TEMPERATURE : float = 0.1

    CROSS_ENCODER_MODEL : str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    CHROMA_COLLECTION : str = "documents"

    DENSE_WEIGHT : float = 0.7
    SPARSE_WEIGHT : float  = 0.3

    EVAL_EMBED_MODEL : str = "all-MiniLM-L6-v2"

    model_config = ConfigDict(env_file = ".env" ,  extra= "ignore")

settings = Settings()
