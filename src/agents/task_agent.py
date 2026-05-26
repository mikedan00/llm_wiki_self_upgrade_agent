from src.agents.base import BaseAgent
from src.core.schemas import AgentResult
from src.prompts.system_prompts import TASK_SYSTEM

class TaskInstanceAgent(BaseAgent):
    name = "TaskInstanceAgent"

    def run(self, task: str, source_text: str, context: str = "") -> AgentResult:
        prompt = f'''
너는 이번 작업만 수행하고 종료되는 인스턴스 에이전트다.

작업:
{task}

원본 자료:
{source_text}

컨텍스트:
{context}

실행 결과를 자세히 작성하라.
'''
        output = self.llm.chat(TASK_SYSTEM, prompt, temperature=0.25, max_tokens=1500)
        return AgentResult(agent_name=self.name, output=output, artifacts=[])
