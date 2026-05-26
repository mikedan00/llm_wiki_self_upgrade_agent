from src.core.config import Settings
from src.core.storage import Storage
from src.core.schemas import RunResult, AgentResult
from src.core.hf_client import HFRouterClient
from src.core.program_manifest import PROGRAM_MANIFEST
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

        context = PROGRAM_MANIFEST + "\n\n" + self.storage.collect_context()

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

        final_prompt = f"""
프로그램 기능 매뉴얼:
{PROGRAM_MANIFEST}

작업:
{task}

에이전트 결과:
{combined}

사용자에게 보여줄 최종 답변을 한국어로 정리하라.
구체적인 기능, 산출물 저장 위치, 다음 실행 방법을 포함하라.
빈 답변은 절대 반환하지 말라.
"""
        try:
            final_answer = self.llm.chat(SUPERVISOR_SYSTEM, final_prompt, temperature=0.2, max_tokens=2200)
        except Exception as e:
            final_answer = ""

        if not final_answer.strip():
            final_answer = self.local_final_answer(task)

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

    def local_final_answer(self, task: str) -> str:
        return f"""
## 이 프로그램으로 할 수 있는 것

이 프로그램은 **LLM Wiki Self-Upgrade Agent**입니다. 사용자의 원본 자료, 오류 로그, 코드, GPT 대화, 프로젝트 메모를 받아서 Obsidian식 Markdown Wiki와 장기기억으로 정리하고, 실행 결과를 평가한 뒤 다음 개선안을 생성하는 시스템입니다.

### 1. 원본 자료 저장
입력한 오류 로그, 코드, 대화 내용, 회의록, 아이디어를 `data/sources`에 저장합니다.

### 2. Obsidian 호환 Wiki 생성
Wiki Agent가 내용을 Markdown 문서로 정리합니다. 결과는 `data/wiki`에 저장됩니다. 이 폴더는 Obsidian Vault로 열 수 있습니다.

### 3. Memory Agent 운영
장기기억, 에피소드 기억, 작업기억을 나누어 `data/memory`에 저장합니다.

### 4. 작업별 Instance Agent 실행
Task Instance Agent가 사용자의 특정 요청을 처리합니다. 예를 들어 오류 분석, 기능 정리, 코드 개선 방향 제안, 배포 문제 해결 등을 수행합니다.

### 5. 결과 평가
Evaluation Agent가 정확성, 완성도, 실행 가능성, 누락 정보, 위험한 자동화 여부를 평가합니다.

### 6. Self-Upgrade 제안
Self-Upgrade Agent가 프롬프트, 메모리 규칙, Wiki 구조, 코드 수정 방향, 학습 데이터 패턴 개선안을 `data/upgrades`에 저장합니다.

### 7. 학습 데이터 생성
Training Data Agent가 향후 LoRA/SFT 학습에 사용할 수 있는 JSONL 데이터를 `data/training/sft_dataset.jsonl`에 축적합니다.

### 8. Hugging Face Router fallback
`HF_ROUTER_MODEL`을 먼저 호출하고 실패하면 `HF_MODEL_CANDIDATES`를 순서대로 호출합니다.

현재 작업: `{task}`

다음 단계는 실제 오류 로그나 프로젝트 문서를 입력해서 Wiki, Memory, Self-Upgrade 결과가 어떻게 생성되는지 확인하는 것입니다.
"""
