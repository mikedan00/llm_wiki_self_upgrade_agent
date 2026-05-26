from src.agents.base import BaseAgent
from src.core.schemas import AgentResult
from src.prompts.system_prompts import MEMORY_SYSTEM

class MemoryAgent(BaseAgent):
    name = "MemoryAgent"

    def run(self, task: str, source_text: str, agent_outputs: str = "") -> AgentResult:
        prompt = f'''
작업:
{task}

원본 자료:
{source_text}

다른 에이전트 결과:
{agent_outputs}

장기기억, 에피소드 기억, 작업기억으로 나누어 Markdown으로 정리하라.
'''
        output = self.llm.chat(MEMORY_SYSTEM, prompt, temperature=0.15, max_tokens=1200)
        filename = f"{self.storage.timestamp()}_memory.md"
        path = self.storage.write_text("memory", filename, output)
        return AgentResult(agent_name=self.name, output=output, artifacts=[str(path)])
