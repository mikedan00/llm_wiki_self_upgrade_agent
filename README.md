# LLM Wiki Self-Upgrade Agent

Obsidian식 Markdown Wiki + LLM Memory + Multi-Agent + Self-Improvement Loop를 결합한 VS Code / Streamlit 배포용 프로젝트입니다.

## 핵심 개념

이 프로젝트는 실제 상용 LLM의 내부 가중치를 즉시 수정하지 않습니다. 대신 다음 구조를 구현합니다.

1. Raw Sources: 원본 대화, 코드, 오류 로그, 문서 저장
2. LLM Wiki: LLM이 원본을 읽고 Markdown 위키로 정리
3. Memory Agent: 장기기억/작업기억/에피소드 기억을 관리
4. Task Instance Agents: 특정 업무를 수행하고 종료되는 임시 에이전트
5. Supervisor Agent: 업무 라우팅과 전체 실행 관리
6. Evaluation Agent: 결과 품질 평가
7. Self-Upgrade Agent: 프롬프트/규칙/위키 구조 개선안 생성
8. Training Data Agent: 향후 LoRA/SFT 학습용 JSONL 데이터셋 축적

## 현실적인 self-upgrade의 의미

가능한 것:

- 프롬프트 개선
- 에이전트 규칙 개선
- 메모리 구조 개선
- 위키 문서 업데이트
- 오류 해결 패턴 축적
- SFT/LoRA 학습 데이터셋 생성
- 수동 검토 후 코드 패치 반영

기본적으로 하지 않는 것:

- 검증 없이 자기 코드 자동 수정
- 검증 없이 LLM 가중치 자동 덮어쓰기
- Hugging Face Inference Provider의 원격 모델 자체를 즉시 재학습

## 설치

```bash
cd llm_wiki_self_upgrade_agent

python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## 환경변수 설정

`.env.example`을 `.env`로 복사합니다.

```bash
copy .env.example .env
```

`.env` 안에 Hugging Face 토큰을 넣습니다.

```env
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxx
HF_MODEL_ID=google/gemma-4-26B-A4B-it
HF_BASE_URL=https://router.huggingface.co/v1
```

Streamlit Cloud에서는 `.env` 대신 Secrets에 넣으세요.

```toml
HF_TOKEN="hf_xxxxxxxxxxxxxxxxx"
HF_MODEL_ID="google/gemma-4-26B-A4B-it"
HF_BASE_URL="https://router.huggingface.co/v1"
```

## 로컬 실행

```bash
streamlit run app.py
```

## CLI 테스트

```bash
python main.py --task "Gemma4 주식 분석 앱의 HF_TOKEN 오류 해결법을 위키로 정리해줘"
```

## Obsidian과 연결

`data/wiki` 폴더를 Obsidian Vault로 열거나, 기존 Vault 안에 이 프로젝트의 `data/wiki`를 복사해서 사용할 수 있습니다.

## 배포 주의

Streamlit Cloud에서는 Gemma 모델을 직접 다운로드하지 않습니다. 이 프로젝트는 Hugging Face Router API 방식으로 호출합니다.
