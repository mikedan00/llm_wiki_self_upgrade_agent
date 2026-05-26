import json
from src.agents.base import BaseAgent
from src.core.schemas import AgentResult
from src.prompts.system_prompts import TRAINING_DATA_SYSTEM

class TrainingDataAgent(BaseAgent):
    name = "TrainingDataAgent"

    def run(self, task: str, source_text: str, final_answer: str, evaluation: str = "") -> AgentResult:
        prompt = f'''
다음 작업 기록을 SFT/LoRA 학습 데이터로 만들기 위한 instruction, input, output 구조로 요약하라.

작업:
{task}

입력:
{source_text}

최종 답변:
{final_answer}

평가:
{evaluation}

JSON 객체 하나만 출력하라.
'''
        raw = self.llm.chat(TRAINING_DATA_SYSTEM, prompt, temperature=0.1, max_tokens=1000)
        record = {
            "instruction": task,
            "input": source_text,
            "output": final_answer,
            "evaluation": evaluation,
            "llm_generated_training_note": raw,
        }
        line = json.dumps(record, ensure_ascii=False)
        path = self.storage.append_text("training", "sft_dataset.jsonl", line + "\n")
        return AgentResult(agent_name=self.name, output=raw, artifacts=[str(path)])
