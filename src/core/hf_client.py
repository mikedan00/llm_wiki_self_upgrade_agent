from openai import OpenAI
from openai import BadRequestError, AuthenticationError, RateLimitError, APIConnectionError, APIStatusError
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
        self.last_model_used: str | None = None

    def chat(
        self,
        system: str,
        user: str,
        temperature: float = 0.2,
        max_tokens: int = 1200,
    ) -> str:
        """
        HF_ROUTER_MODEL을 먼저 호출하고, 실패하거나 빈 응답이면 HF_MODEL_CANDIDATES를 순서대로 fallback 호출한다.
        """
        errors: list[str] = []
        empty_models: list[str] = []

        for model in self.settings.candidate_models:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                content = response.choices[0].message.content or ""
                content = content.strip()
                if content:
                    self.last_model_used = model
                    return content

                empty_models.append(model)
                continue

            except BadRequestError as e:
                errors.append(f"[BadRequestError] model={model}\n{str(e)}")
                continue

            except RateLimitError as e:
                errors.append(f"[RateLimitError] model={model}\n{str(e)}")
                continue

            except APIStatusError as e:
                errors.append(f"[APIStatusError] model={model}, status={e.status_code}\n{str(e)}")
                continue

            except APIConnectionError as e:
                errors.append(f"[APIConnectionError] model={model}\n{str(e)}")
                continue

            except AuthenticationError as e:
                raise RuntimeError(
                    "Hugging Face 인증 오류입니다. HF_TOKEN이 잘못되었거나 만료되었을 수 있습니다.\n\n"
                    f"현재 Base URL: {self.settings.hf_base_url}\n"
                    f"원본 오류:\n{str(e)}"
                ) from e

        if empty_models and not errors:
            raise RuntimeError(
                "모든 후보 모델이 빈 응답을 반환했습니다.\n\n"
                f"빈 응답 모델 목록:\n- " + "\n- ".join(empty_models) +
                "\n\n해결 방법:\n"
                "1. max_tokens를 늘리거나 temperature를 낮추세요.\n"
                "2. HF_ROUTER_MODEL을 다른 provider로 바꿔보세요.\n"
                "3. Qwen fallback 모델을 우선순위 위쪽으로 올려 테스트하세요."
            )

        raise RuntimeError(
            "모든 Hugging Face Router 후보 모델 호출에 실패했습니다.\n\n"
            "확인할 항목:\n"
            "1. Streamlit Secrets의 HF_TOKEN 값\n"
            "2. HF_ROUTER_MODEL에 provider suffix가 포함되어 있는지\n"
            "3. HF_MODEL_CANDIDATES 후보 모델들이 현재 provider에서 지원되는지\n"
            "4. Gemma 라이선스 동의 여부\n"
            "5. Hugging Face Inference Provider 사용 가능 여부\n\n"
            f"Base URL: {self.settings.hf_base_url}\n"
            f"시도한 모델 목록:\n- " + "\n- ".join(self.settings.candidate_models) +
            "\n\n빈 응답 모델:\n- " + "\n- ".join(empty_models) +
            "\n\n오류 로그:\n" + "\n\n".join(errors[-8:])
        )
