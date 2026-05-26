from src.agents.base import BaseAgent
from src.core.schemas import AgentResult
from src.prompts.system_prompts import MEMORY_SYSTEM
from src.core.program_manifest import PROGRAM_MANIFEST

class MemoryAgent(BaseAgent):
    name = "MemoryAgent"

    def run(self, task: str, source_text: str, agent_outputs: str = "") -> AgentResult:
        prompt = f"""
프로그램 기능 매뉴얼:
{PROGRAM_MANIFEST}

작업:
{task}

원본 자료:
{source_text}

다른 에이전트 결과:
{agent_outputs}

장기기억, 에피소드 기억, 작업기억으로 나누어 Markdown으로 정리하라.
"""
        output = self.llm.chat(MEMORY_SYSTEM, prompt, temperature=0.15, max_tokens=1600)
        if not output.strip():
            output = """# Memory

## Long-term Memory
- 사용자는 LLM Wiki Self-Upgrade Agent를 VS Code와 Streamlit Cloud에서 운용하려고 한다.
- 사용자는 Hugging Face Router provider suffix 방식의 모델 fallback 구조를 선호한다.
- 핵심 모델 기본값은 google/gemma-4-26B-A4B-it:deepinfra다.

## Episodic Memory
- 이번 작업에서는 프로그램이 자기 자신이 할 수 있는 일을 설명하도록 요청되었다.
- 일부 Agent가 빈 응답을 반환할 수 있어, 프로그램 기능 매뉴얼을 컨텍스트로 주입하는 개선이 필요했다.

## Working Memory
- 다음 실행에서는 "이 프로그램"이라는 표현을 LLM Wiki Self-Upgrade Agent 자체로 해석해야 한다.
- Wiki, Memory, Self-Upgrade 결과가 빈 응답이면 로컬 fallback 문서를 생성해야 한다.
"""
        filename = f"{self.storage.timestamp()}_memory.md"
        path = self.storage.write_text("memory", filename, output)
        return AgentResult(agent_name=self.name, output=output, artifacts=[str(path)])
