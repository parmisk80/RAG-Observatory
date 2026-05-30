from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    APP_NAME : str
    API_V1_PREFIX : str

    DEBUG : bool = False

    DATABASE_URL : str
    REDIS_URL : str
    CHROMA_HOST : str
    CHROMA_PORT : int
    CELERY_BROKER_URL : str
    CELERY_BACKEND_URL : str

    LOG_LEVEL : str = "INFO"

    OLLAMA_EMBED_MODEL : str = "nomic-embed-text" 
    OLLAMA_BASE_URL : str = "http://localhost:11434"

    model_config = ConfigDict(env_file = ".env" ,  extra= "ignore")

settings = Settings()
    