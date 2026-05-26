PROGRAM_MANIFEST = """
# LLM Wiki Self-Upgrade Agent 기능 매뉴얼

## 프로그램 정체
이 프로그램은 Obsidian식 Markdown Wiki, 장기기억 Memory, 작업별 Instance Agent, 평가 Agent, 자기개선 Agent, 학습데이터 생성 Agent를 결합한 개인 지식관리/자기개선형 LLM Agent 시스템이다.

## 사용자가 이 프로그램으로 할 수 있는 것

### 1. 원본 자료 저장
사용자는 오류 로그, 코드, GPT 대화, 회의록, 아이디어, 문서 내용을 입력할 수 있다.
입력된 원본 자료는 data/sources 폴더에 저장된다.

### 2. LLM Wiki 생성
Wiki Agent는 입력 자료와 작업 내용을 바탕으로 Obsidian 호환 Markdown Wiki 문서를 만든다.
문서는 data/wiki 폴더에 저장된다.
관련 개념은 [[링크]] 형식으로 연결할 수 있다.
Obsidian에서 data/wiki 폴더를 열면 개인 지식베이스처럼 탐색할 수 있다.

### 3. Memory 관리
Memory Agent는 정보를 세 종류로 나눈다.
- Long-term Memory: 장기간 재사용할 프로젝트, 선호, 기술스택, 반복 패턴
- Episodic Memory: 이번 작업에서 발생한 사건, 결과, 오류, 결정
- Working Memory: 다음 작업에서 바로 사용할 임시 상태

저장 위치는 data/memory다.

### 4. 작업별 Instance Agent 실행
Task Instance Agent는 사용자의 특정 작업 하나를 수행하고 종료되는 임시 에이전트다.
예:
- 오류 로그 분석
- 프로그램 기능 정리
- 프로젝트 설계 정리
- 코드 개선 방향 제안
- 배포 문제 해결
- 문서 요약
- 아이디어 구조화

### 5. 평가
Evaluation Agent는 결과를 정확성, 완성도, 실행 가능성, 누락 정보, 위험한 자동화 여부, 개선 포인트로 평가한다.

### 6. Self-Upgrade 제안
Self-Upgrade Agent는 다음 실행에서 시스템이 더 좋아지도록 개선안을 만든다.
예:
- 프롬프트 개선
- 메모리 규칙 개선
- Wiki 구조 개선
- 코드 수정 제안
- 학습 데이터로 추가할 패턴
- 사람이 검토해야 할 항목

저장 위치는 data/upgrades다.

### 7. 학습 데이터 축적
Training Data Agent는 작업 입력, 최종 답변, 평가 결과를 SFT/LoRA 학습용 JSONL 형태로 저장한다.
저장 위치는 data/training/sft_dataset.jsonl이다.

### 8. HF Router 모델 fallback
이 프로그램은 HF_ROUTER_MODEL을 먼저 호출하고, 실패하면 HF_MODEL_CANDIDATES를 순서대로 시도한다.
예:
- google/gemma-4-26B-A4B-it:deepinfra
- google/gemma-4-26B-A4B-it:novita
- google/gemma-4-31B-it:deepinfra
- google/gemma-4-31B-it:together
- Qwen/Qwen3.5-9B:together
- Qwen/Qwen2.5-7B-Instruct:together

### 9. VS Code와 Streamlit 사용
로컬에서는 VS Code에서 실행할 수 있다.
배포는 Streamlit Cloud에서 app.py를 main file로 지정하면 된다.
HF_TOKEN은 .env 또는 Streamlit Secrets에서 읽는다.

## 이 프로그램의 한계
- 원격 Hugging Face Provider의 모델 가중치를 즉시 자동 수정하지 않는다.
- 실제 LLM 가중치 학습은 별도 LoRA/SFT 파이프라인으로 분리해야 한다.
- Self-Upgrade는 검증 가능한 개선안, 프롬프트 개선, 메모리 개선, 학습 데이터 생성까지를 기본 범위로 한다.
- 코드 자동 수정은 사람이 검토한 뒤 반영하는 구조가 안전하다.

## 가장 적합한 사용 사례
- GPT 대화와 프로젝트 기록을 Obsidian식 Wiki로 정리
- Streamlit/GitHub/HF_TOKEN 오류 해결 기록 축적
- AI 에이전트 프로젝트의 장기 기억 구축
- 반복 개발 작업의 지식베이스화
- 향후 LoRA/SFT 학습용 데이터셋 축적
- 개인 제2의 뇌 시스템 구축
"""
