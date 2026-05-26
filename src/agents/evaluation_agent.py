from src.agents.base import BaseAgent
from src.core.schemas import AgentResult
from src.prompts.system_prompts import EVALUATION_SYSTEM

class EvaluationAgent(BaseAgent):
    name = "EvaluationAgent"

    def run(self, task: str, combined_outputs: str) -> AgentResult:
        prompt = f'''
작업:
{task}

에이전트 결과:
{combined_outputs}

품질을 평가하고 개선 포인트를 작성하라.
'''
        output = self.llm.chat(EVALUATION_SYSTEM, prompt, temperature=0.1, max_tokens=1000)
        return AgentResult(agent_name=self.name, output=output, artifacts=[])
