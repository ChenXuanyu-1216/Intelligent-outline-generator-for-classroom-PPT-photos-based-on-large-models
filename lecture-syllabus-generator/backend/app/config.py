from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    baseline_version: str = "MVP Design v1.1 / PRD v1.1"
    app_name: str = "课堂PPT照片智能大纲生成器"

    model_provider: str = "mock"
    model_api_key: str = ""
    model_base_url: str = "https://api.openai.com/v1"
    model_name: str = "gpt-4o-mini"
    model_timeout_seconds: int = 60
    model_max_retry: int = 1

    allowed_ext: str = ".jpg,.jpeg,.png,.pdf"
    max_file_mb: int = 10
    max_files_per_batch: int = 20
    recommended_batch: int = 10
    low_confidence_threshold: float = 0.60

    database_url: str = "sqlite:///./data/app.db"
    storage_dir: str = "storage"
    prompts_dir: str = "prompts"

    class Config:
        env_prefix = "APP_"
        env_file = ".env"

    @property
    def allowed_ext_list(self) -> list[str]:
        return [e.strip().lower() for e in self.allowed_ext.split(",") if e.strip()]


settings = Settings()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STORAGE_DIR = BASE_DIR / settings.storage_dir
PROMPTS_DIR = BASE_DIR / settings.prompts_dir
FRONTEND_DIR = BASE_DIR.parent / "frontend"

DATA_DIR.mkdir(parents=True, exist_ok=True)
STORAGE_DIR.mkdir(parents=True, exist_ok=True)