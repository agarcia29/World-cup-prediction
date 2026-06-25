from functools import lru_cache
from pathlib import Path
import os
from pydantic import BaseModel
from src.utils.constants import MODELS_DIR, PROCESSED_DIR, DATA_DIR

class Settings(BaseModel):
    app_name: str = 'World Cup Predictor API'
    models_dir: Path = MODELS_DIR
    processed_dir: Path = PROCESSED_DIR
    data_dir: Path = DATA_DIR
    app_env: str = os.getenv('APP_ENV', os.getenv('ENV', 'development')).lower()
    disable_heavy_bayes: bool = os.getenv('DISABLE_HEAVY_BAYES', 'false').lower() == 'true'
    enable_async_jobs: bool = os.getenv('ENABLE_ASYNC_JOBS', 'true').lower() == 'true'

    @property
    def is_production(self) -> bool:
        return self.app_env == 'production'

@lru_cache
def get_settings() -> Settings:
    return Settings()