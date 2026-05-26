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

with st.sidebar:
    st.header("LLM 설정")
    hf_token_input = st.text_input("HF_TOKEN", type="password", value="")
    model_id = st.text_input("Model ID", value=os.getenv("HF_MODEL_ID", "google/gemma-4-26B-A4B-it"))
    base_url = st.text_input("HF Router Base URL", value=os.getenv("HF_BASE_URL", "https://router.huggingface.co/v1"))
    data_dir = st.text_input("Data Directory", value=os.getenv("APP_DATA_DIR", "data"))

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
    base_url_override=base_url,
    data_dir_override=data_dir,
)

tabs = st.tabs(["작업 실행", "Wiki", "Memory", "Runs", "Upgrades", "Training Data", "설계 설명"])

with tabs[0]:
    st.subheader("작업 실행")
    task = st.text_area(
        "Agent에게 시킬 작업",
        height=120,
        placeholder="예: 최근 Streamlit HF_TOKEN 오류 해결 과정을 위키와 기억으로 정리하고, 다음 개선안을 만들어줘.",
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

이 구조의 self-upgrade는 다음 순서로 작동합니다.

1. 작업 수행
2. 결과와 중간 산출물 저장
3. 평가 Agent가 품질/누락/오류 위험을 평가
4. Self-Upgrade Agent가 규칙, 프롬프트, 메모리 구조 개선안 생성
5. Training Data Agent가 좋은 질의응답/작업흐름을 JSONL로 저장
6. 사람이 검토 후 프롬프트/코드/LoRA 학습에 반영

원격 Hugging Face Provider의 모델 가중치를 직접 수정하지는 않습니다. 대신 학습 가능한 데이터와 개선 루프를 축적합니다.
"""
    )
