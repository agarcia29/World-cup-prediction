from functools import lru_cache
from pathlib import Path
from pydantic import BaseModel
from src.utils.constants import MODELS_DIR, PROCESSED_DIR

class Settings(BaseModel):
    app_name: str = 'World Cup Predictor API'
    models_dir: Path = MODELS_DIR
    processed_dir: Path = PROCESSED_DIR

@lru_cache
def get_settings() -> Settings:
    return Settings()
