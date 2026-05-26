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
    hf_router_model: str = "google/gemma-4-26B-A4B-it:deepinfra"
    hf_model_candidates: str = (
        "google/gemma-4-26B-A4B-it:deepinfra,"
        "google/gemma-4-26B-A4B-it:novita,"
        "google/gemma-4-31B-it:deepinfra,"
        "google/gemma-4-31B-it:together,"
        "Qwen/Qwen3.5-9B:together,"
        "Qwen/Qwen2.5-7B-Instruct:together"
    )
    hf_base_url: str = "https://router.huggingface.co/v1"
    app_data_dir: str = "data"

    @property
    def data_path(self) -> Path:
        return Path(self.app_data_dir)

    @property
    def candidate_models(self) -> list[str]:
        """HF_ROUTER_MODEL을 최우선으로 두고, HF_MODEL_CANDIDATES를 fallback으로 사용."""
        models: list[str] = []
        if self.hf_router_model.strip():
            models.append(self.hf_router_model.strip())

        for item in self.hf_model_candidates.split(","):
            model = item.strip()
            if model and model not in models:
                models.append(model)

        # 마지막 fallback으로 provider suffix 없는 기본 모델도 넣는다.
        if self.hf_model_id.strip() and self.hf_model_id.strip() not in models:
            models.append(self.hf_model_id.strip())

        return models


def get_settings(
    hf_token_override: str | None = None,
    model_id_override: str | None = None,
    router_model_override: str | None = None,
    candidates_override: str | None = None,
    base_url_override: str | None = None,
    data_dir_override: str | None = None,
) -> Settings:
    return Settings(
        hf_token=hf_token_override or get_secret_or_env("HF_TOKEN", ""),
        hf_model_id=model_id_override or get_secret_or_env("HF_MODEL_ID", "google/gemma-4-26B-A4B-it"),
        hf_router_model=router_model_override or get_secret_or_env("HF_ROUTER_MODEL", "google/gemma-4-26B-A4B-it:deepinfra"),
        hf_model_candidates=candidates_override or get_secret_or_env(
            "HF_MODEL_CANDIDATES",
            "google/gemma-4-26B-A4B-it:deepinfra,"
            "google/gemma-4-26B-A4B-it:novita,"
            "google/gemma-4-31B-it:deepinfra,"
            "google/gemma-4-31B-it:together,"
            "Qwen/Qwen3.5-9B:together,"
            "Qwen/Qwen2.5-7B-Instruct:together",
        ),
        hf_base_url=base_url_override or get_secret_or_env("HF_BASE_URL", "https://router.huggingface.co/v1"),
        app_data_dir=data_dir_override or get_secret_or_env("APP_DATA_DIR", "data"),
    )
