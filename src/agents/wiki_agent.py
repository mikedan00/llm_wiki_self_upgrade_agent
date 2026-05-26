from src.agents.base import BaseAgent
from src.core.schemas import AgentResult
from src.core.utils import slugify_kor
from src.prompts.system_prompts import WIKI_SYSTEM
from src.core.program_manifest import PROGRAM_MANIFEST

class WikiAgent(BaseAgent):
    name = "WikiAgent"

    def run(self, task: str, source_text: str, context: str = "") -> AgentResult:
        prompt = f"""
프로그램 기능 매뉴얼:
{PROGRAM_MANIFEST}

작업:
{task}

기존 Wiki/Memory 컨텍스트:
{context}

새 원본 자료:
{source_text}

위 내용을 바탕으로 Obsidian 호환 Markdown Wiki 문서를 작성하라.
"""
        output = self.llm.chat(WIKI_SYSTEM, prompt, temperature=0.2, max_tokens=2200)
        if not output.strip():
            output = f"""# LLM Wiki Self-Upgrade Agent 기능 정리

## 요약
이 문서는 LLM Wiki Self-Upgrade Agent가 수행할 수 있는 기능을 정리한다.

## 핵심 내용
{PROGRAM_MANIFEST}

## 관련 개념
- [[LLM Wiki]]
- [[Obsidian]]
- [[Memory Agent]]
- [[Self-Upgrade Agent]]
- [[Hugging Face Router]]

## 관련 프로젝트
- [[VS Code Streamlit Agent]]
- [[Obsidian 제2의 뇌]]
- [[LoRA SFT 학습 데이터]]

## 다음 행동
- 실제 오류 로그를 입력하여 Wiki/Memory 저장을 테스트한다.
- data/wiki 폴더를 Obsidian Vault로 열어본다.
- Training Data를 축적한 뒤 LoRA/SFT 파이프라인으로 확장한다.

## 출처/근거
- 프로그램 내부 기능 매뉴얼
- 현재 프로젝트 코드 구조
"""
        filename = f"{self.storage.timestamp()}_{slugify_kor(task)}.md"
        path = self.storage.write_text("wiki", filename, output)
        return AgentResult(agent_name=self.name, output=output, artifacts=[str(path)])
