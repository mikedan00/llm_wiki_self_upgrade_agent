from src.agents.base import BaseAgent
from src.core.schemas import AgentResult
from src.prompts.system_prompts import TASK_SYSTEM
from src.core.program_manifest import PROGRAM_MANIFEST

class TaskInstanceAgent(BaseAgent):
    name = "TaskInstanceAgent"

    def run(self, task: str, source_text: str, context: str = "") -> AgentResult:
        prompt = f"""
프로그램 기능 매뉴얼:
{PROGRAM_MANIFEST}

너는 이번 작업만 수행하고 종료되는 인스턴스 에이전트다.

작업:
{task}

원본 자료:
{source_text}

기존 Wiki/Memory 컨텍스트:
{context}

실행 결과를 자세히 작성하라.
특히 사용자가 이 프로그램으로 무엇을 할 수 있는지 묻는 경우, 기능 매뉴얼을 바탕으로 구체적으로 설명하라.
"""
        output = self.llm.chat(TASK_SYSTEM, prompt, temperature=0.2, max_tokens=2200)
        if not output.strip():
            output = self.local_capability_summary()
        return AgentResult(agent_name=self.name, output=output, artifacts=[])

    def local_capability_summary(self) -> str:
        return """
# 이 프로그램으로 할 수 있는 것

이 프로그램은 LLM Wiki Self-Upgrade Agent입니다.

## 주요 기능
1. 원본 자료를 저장합니다.
2. 원본 자료를 Obsidian 호환 Markdown Wiki로 정리합니다.
3. 장기기억, 에피소드 기억, 작업기억을 분리해 저장합니다.
4. 특정 업무를 Task Instance Agent가 수행합니다.
5. 결과를 Evaluation Agent가 평가합니다.
6. Self-Upgrade Agent가 다음 실행을 위한 개선안을 만듭니다.
7. Training Data Agent가 SFT/LoRA 학습용 JSONL 데이터를 축적합니다.
8. Hugging Face Router 모델을 provider suffix 방식으로 호출하고 fallback을 수행합니다.

## 저장 위치
- data/sources: 원본 자료
- data/wiki: Wiki 문서
- data/memory: Memory 문서
- data/runs: 실행 로그
- data/upgrades: 자기개선 제안
- data/training: 학습 데이터
"""
