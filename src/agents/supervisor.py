from src.core.config import Settings
from src.core.storage import Storage
from src.core.schemas import RunResult, AgentResult
from src.core.hf_client import HFRouterClient
from src.prompts.system_prompts import SUPERVISOR_SYSTEM
from src.agents.wiki_agent import WikiAgent
from src.agents.memory_agent import MemoryAgent
from src.agents.task_agent import TaskInstanceAgent
from src.agents.evaluation_agent import EvaluationAgent
from src.agents.self_upgrade_agent import SelfUpgradeAgent
from src.agents.training_data_agent import TrainingDataAgent

class SupervisorAgent:
    def __init__(self, settings: Settings, enabled: dict | None = None):
        self.settings = settings
        self.storage = Storage(settings)
        self.llm = HFRouterClient(settings)
        self.enabled = enabled or {
            "wiki": True,
            "memory": True,
            "evaluation": True,
            "self_upgrade": True,
            "training": True,
        }

    def run(self, task: str, source_text: str = "") -> RunResult:
        run_id = self.storage.timestamp()
        artifacts = []
        agent_results: list[AgentResult] = []

        if source_text.strip():
            src_path = self.storage.write_text("sources", f"{run_id}_source.md", source_text)
            artifacts.append(str(src_path))

        context = self.storage.collect_context()

        task_agent = TaskInstanceAgent(self.settings)
        task_result = task_agent.run(task=task, source_text=source_text, context=context)
        agent_results.append(task_result)

        if self.enabled.get("wiki", True):
            wiki_result = WikiAgent(self.settings).run(task=task, source_text=source_text, context=context)
            agent_results.append(wiki_result)
            artifacts.extend(wiki_result.artifacts)

        combined = "\n\n".join([f"## {r.agent_name}\n{r.output}" for r in agent_results])

        if self.enabled.get("memory", True):
            memory_result = MemoryAgent(self.settings).run(task=task, source_text=source_text, agent_outputs=combined)
            agent_results.append(memory_result)
            artifacts.extend(memory_result.artifacts)
            combined += f"\n\n## {memory_result.agent_name}\n{memory_result.output}"

        evaluation_text = None
        if self.enabled.get("evaluation", True):
            eval_result = EvaluationAgent(self.settings).run(task=task, combined_outputs=combined)
            agent_results.append(eval_result)
            evaluation_text = eval_result.output
            combined += f"\n\n## {eval_result.agent_name}\n{eval_result.output}"

        upgrade_text = None
        if self.enabled.get("self_upgrade", True):
            up_result = SelfUpgradeAgent(self.settings).run(
                task=task,
                combined_outputs=combined,
                evaluation=evaluation_text or "",
            )
            agent_results.append(up_result)
            upgrade_text = up_result.output
            artifacts.extend(up_result.artifacts)

        final_prompt = f'''
작업:
{task}

에이전트 결과:
{combined}

사용자에게 보여줄 최종 답변을 한국어로 정리하라.
구체적인 산출물, 저장된 위치, 다음 실행 방법을 포함하라.
'''
        final_answer = self.llm.chat(SUPERVISOR_SYSTEM, final_prompt, temperature=0.2, max_tokens=1400)

        if self.enabled.get("training", True):
            train_result = TrainingDataAgent(self.settings).run(
                task=task,
                source_text=source_text,
                final_answer=final_answer,
                evaluation=evaluation_text or "",
            )
            agent_results.append(train_result)
            artifacts.extend(train_result.artifacts)

        result = RunResult(
            run_id=run_id,
            task=task,
            final_answer=final_answer,
            agent_results=agent_results,
            evaluation=evaluation_text,
            upgrade_proposal=upgrade_text,
            artifacts=artifacts,
        )
        self.storage.write_json("runs", f"{run_id}_run.json", result.model_dump())
        return result
