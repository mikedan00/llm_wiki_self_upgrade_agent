import os
import streamlit as st
import pandas as pd
from src.core.config import get_settings
from src.core.storage import Storage
from src.agents.supervisor import SupervisorAgent

st.set_page_config(
    page_title="LLM Wiki Self-Upgrade Agent",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 LLM Wiki Self-Upgrade Agent")
st.caption("Obsidian식 Markdown Wiki + Memory Agent + Task Instance Agents + Self-Upgrade Loop")

DEFAULT_CANDIDATES = (
    "google/gemma-4-26B-A4B-it:deepinfra,"
    "google/gemma-4-26B-A4B-it:novita,"
    "google/gemma-4-31B-it:deepinfra,"
    "google/gemma-4-31B-it:together,"
    "Qwen/Qwen3.5-9B:together,"
    "Qwen/Qwen2.5-7B-Instruct:together"
)

with st.sidebar:
    st.header("LLM 설정")

    hf_token_input = st.text_input(
        "HF_TOKEN",
        type="password",
        value="",
        help="Streamlit Secrets에 HF_TOKEN을 넣었다면 비워두어도 됩니다.",
    )

    model_id = st.text_input(
        "HF_MODEL_ID",
        value=os.getenv("HF_MODEL_ID", "google/gemma-4-26B-A4B-it"),
        help="provider suffix 없는 기본 모델 ID입니다.",
    )

    router_model = st.text_input(
        "HF_ROUTER_MODEL",
        value=os.getenv("HF_ROUTER_MODEL", "google/gemma-4-26B-A4B-it:deepinfra"),
        help="가장 먼저 호출할 Hugging Face Router 모델입니다. 예: model:deepinfra",
    )

    candidates = st.text_area(
        "HF_MODEL_CANDIDATES",
        value=os.getenv("HF_MODEL_CANDIDATES", DEFAULT_CANDIDATES),
        height=110,
        help="쉼표로 구분된 fallback 모델 목록입니다.",
    )

    base_url = st.text_input(
        "HF Router Base URL",
        value=os.getenv("HF_BASE_URL", "https://router.huggingface.co/v1"),
    )

    data_dir = st.text_input(
        "Data Directory",
        value=os.getenv("APP_DATA_DIR", "data"),
    )

    st.divider()
    st.markdown("### 실행 옵션")
    run_wiki = st.checkbox("Wiki Agent 실행", value=True)
    run_memory = st.checkbox("Memory Agent 실행", value=True)
    run_eval = st.checkbox("Evaluation Agent 실행", value=True)
    run_upgrade = st.checkbox("Self-Upgrade Agent 실행", value=True)
    run_training = st.checkbox("Training Data Agent 실행", value=True)

    st.divider()
    st.info("Streamlit Cloud에서는 HF_TOKEN을 Secrets에 넣는 것을 권장합니다.")

settings = get_settings(
    hf_token_override=hf_token_input or None,
    model_id_override=model_id,
    router_model_override=router_model,
    candidates_override=candidates,
    base_url_override=base_url,
    data_dir_override=data_dir,
)

tabs = st.tabs(["작업 실행", "Wiki", "Memory", "Runs", "Upgrades", "Training Data", "설계 설명"])

with tabs[0]:
    st.subheader("작업 실행")

    with st.expander("현재 모델 라우터 설정", expanded=False):
        st.write("우선 호출 모델:", settings.hf_router_model)
        st.write("Fallback 후보:")
        st.code("\n".join(settings.candidate_models))

    task = st.text_area(
        "Agent에게 시킬 작업",
        height=120,
        placeholder="예: 배터리 오스모 속도를 줄이는 방법을 찾아 정리해줘",
    )
    source_text = st.text_area(
        "추가 원본 자료 / 오류 로그 / 코드 / 대화 내용",
        height=180,
        placeholder="여기에 원본 로그, 코드, GPT 대화, 회의록 등을 붙여넣으세요.",
    )

    if st.button("실행", type="primary"):
        if not task.strip():
            st.warning("작업 내용을 입력하세요.")
        else:
            try:
                with st.spinner("에이전트들이 작업 중입니다..."):
                    supervisor = SupervisorAgent(
                        settings,
                        enabled={
                            "wiki": run_wiki,
                            "memory": run_memory,
                            "evaluation": run_eval,
                            "self_upgrade": run_upgrade,
                            "training": run_training,
                        },
                    )
                    result = supervisor.run(task=task, source_text=source_text)

                st.success(f"완료: {result.run_id}")
                st.markdown("## 최종 응답")
                st.write(result.final_answer)

                st.markdown("## 실행 요약")
                st.json(result.model_dump())

            except Exception as e:
                st.error("실행 중 오류가 발생했습니다.")
                st.code(str(e))

with tabs[1]:
    st.subheader("Wiki 문서")
    storage = Storage(settings)
    wiki_files = storage.list_files("wiki", suffix=".md")
    selected = st.selectbox("Wiki 파일 선택", wiki_files)
    if selected:
        st.markdown(storage.read_relative(selected))

with tabs[2]:
    st.subheader("Memory")
    storage = Storage(settings)
    mem_files = storage.list_files("memory", suffix=".md")
    selected = st.selectbox("Memory 파일 선택", mem_files)
    if selected:
        st.markdown(storage.read_relative(selected))

with tabs[3]:
    st.subheader("Run Logs")
    storage = Storage(settings)
    run_files = storage.list_files("runs", suffix=".json")
    if run_files:
        df = pd.DataFrame({"file": run_files})
        st.dataframe(df, use_container_width=True)
        selected = st.selectbox("Run 파일 선택", run_files)
        if selected:
            st.json(storage.read_json_relative(selected))
    else:
        st.info("아직 실행 로그가 없습니다.")

with tabs[4]:
    st.subheader("Self-Upgrade Proposals")
    storage = Storage(settings)
    upgrade_files = storage.list_files("upgrades", suffix=".md")
    selected = st.selectbox("개선안 선택", upgrade_files)
    if selected:
        st.markdown(storage.read_relative(selected))

with tabs[5]:
    st.subheader("Training Data")
    storage = Storage(settings)
    train_files = storage.list_files("training", suffix=".jsonl")
    selected = st.selectbox("학습 데이터 파일 선택", train_files)
    if selected:
        content = storage.read_relative(selected)
        st.code(content[:12000], language="jsonl")

with tabs[6]:
    st.subheader("아키텍처")
    st.markdown(
        """
```text
User Task
  ↓
Supervisor Agent
  ├─ Wiki Agent: sources → Markdown Wiki
  ├─ Memory Agent: long-term / episodic / working memory
  ├─ Task Instance Agent: 업무별 임시 실행자
  ├─ Evaluation Agent: 품질 평가
  ├─ Self-Upgrade Agent: 프롬프트/규칙/구조 개선안 생성
  └─ Training Data Agent: SFT/LoRA용 JSONL 축적
```

HF Router 호출 방식은 다음 순서입니다.

1. HF_ROUTER_MODEL 먼저 호출
2. 실패하면 HF_MODEL_CANDIDATES를 왼쪽부터 순서대로 fallback
3. 모든 후보가 실패하면 실패한 모델별 오류를 화면에 표시

예:

```text
HF_ROUTER_MODEL=google/gemma-4-26B-A4B-it:deepinfra
HF_MODEL_CANDIDATES=google/gemma-4-26B-A4B-it:deepinfra,google/gemma-4-26B-A4B-it:novita,...
```
"""
    )
