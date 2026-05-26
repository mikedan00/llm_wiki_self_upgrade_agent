from openai import OpenAI
from src.core.config import Settings

class HFRouterClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        if not settings.hf_token:
            raise ValueError("HF_TOKEN이 없습니다. .env 또는 Streamlit Secrets/Sidebar에 입력하세요.")
        self.client = OpenAI(
            base_url=settings.hf_base_url,
            api_key=settings.hf_token,
        )

    def chat(
        self,
        system: str,
        user: str,
        temperature: float = 0.2,
        max_tokens: int = 1200,
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.settings.hf_model_id,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""
