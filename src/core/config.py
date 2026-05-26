from pathlib import Path
import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

try:
    import streamlit as st
except Exception:
    st = None


def get_secret_or_env(key: str, default: str = "") -> str:
    """
    우선순위:
    1. Streamlit Secrets
    2. 환경변수 / .env
    3. 기본값
    """
    if st is not None:
        try:
            if key in st.secrets:
                return str(st.secrets[key])
        except Exception:
            pass
    return os.getenv(key, default)


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
        hf_token=hf_token_override or get_secret_or_env("HF_TOKEN", ""),
        hf_model_id=model_id_override or get_secret_or_env("HF_MODEL_ID", "google/gemma-4-26B-A4B-it"),
        hf_base_url=base_url_override or get_secret_or_env("HF_BASE_URL", "https://router.huggingface.co/v1"),
        app_data_dir=data_dir_override or get_secret_or_env("APP_DATA_DIR", "data"),
    )