from src.agents.base import BaseAgent
from src.core.schemas import AgentResult
from src.core.utils import slugify_kor
from src.prompts.system_prompts import WIKI_SYSTEM

class WikiAgent(BaseAgent):
    name = "WikiAgent"

    def run(self, task: str, source_text: str, context: str = "") -> AgentResult:
        prompt = f'''
작업:
{task}

기존 Wiki/Memory 컨텍스트:
{context}

새 원본 자료:
{source_text}

위 내용을 바탕으로 Obsidian 호환 Markdown Wiki 문서를 작성하라.
'''
        output = self.llm.chat(WIKI_SYSTEM, prompt, temperature=0.2, max_tokens=1600)
        filename = f"{self.storage.timestamp()}_{slugify_kor(task)}.md"
        path = self.storage.write_text("wiki", filename, output)
        return AgentResult(agent_name=self.name, output=output, artifacts=[str(path)])
