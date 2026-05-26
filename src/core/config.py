from pathlib import Path
import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class Settings(BaseModel):
    hf_token: str = ""
    hf_model_id: str = "google/gemma-4-26B-A4B-it"
    hf_base_url: str = "https://router.huggingface.co/v1"
    app_data_dir: str = "data"

    @property
    def data_path(self) -> Path:
        return Path(self.app_data_dir)

def get_settings(
    hf_token_override: str | None = None,
    model_id_override: str | None = None,
    base_url_override: str | None = None,
    data_dir_override: str | None = None,
) -> Settings:
    return Settings(
        hf_token=hf_token_override or os.getenv("HF_TOKEN", ""),
        hf_model_id=model_id_override or os.getenv("HF_MODEL_ID", "google/gemma-4-26B-A4B-it"),
        hf_base_url=base_url_override or os.getenv("HF_BASE_URL", "https://router.huggingface.co/v1"),
        app_data_dir=data_dir_override or os.getenv("APP_DATA_DIR", "data"),
    )
