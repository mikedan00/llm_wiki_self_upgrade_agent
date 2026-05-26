from src.agents.base import BaseAgent
from src.core.schemas import AgentResult
from src.prompts.system_prompts import SELF_UPGRADE_SYSTEM

class SelfUpgradeAgent(BaseAgent):
    name = "SelfUpgradeAgent"

    def run(self, task: str, combined_outputs: str, evaluation: str = "") -> AgentResult:
        prompt = f'''
작업:
{task}

에이전트 결과:
{combined_outputs}

평가:
{evaluation}

다음 실행에서 시스템이 더 좋아지도록 자기개선 제안을 작성하라.
검증 없이 자동 반영하지 말고, 사람이 검토할 수 있는 개선안으로 작성하라.
'''
        output = self.llm.chat(SELF_UPGRADE_SYSTEM, prompt, temperature=0.2, max_tokens=1400)
        filename = f"{self.storage.timestamp()}_upgrade_proposal.md"
        path = self.storage.write_text("upgrades", filename, output)
        return AgentResult(agent_name=self.name, output=output, artifacts=[str(path)])
