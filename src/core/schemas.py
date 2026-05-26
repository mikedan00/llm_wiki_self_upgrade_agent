from pydantic import BaseModel, Field

class AgentResult(BaseModel):
    agent_name: str
    output: str
    artifacts: list[str] = Field(default_factory=list)

class RunResult(BaseModel):
    run_id: str
    task: str
    final_answer: str
    agent_results: list[AgentResult]
    evaluation: str | None = None
    upgrade_proposal: str | None = None
    artifacts: list[str] = Field(default_factory=list)
