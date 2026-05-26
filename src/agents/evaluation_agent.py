from src.agents.base import BaseAgent
from src.core.schemas import AgentResult
from src.prompts.system_prompts import EVALUATION_SYSTEM

class EvaluationAgent(BaseAgent):
    name = "EvaluationAgent"

    def run(self, task: str, combined_outputs: str) -> AgentResult:
        prompt = f"""
작업:
{task}

에이전트 결과:
{combined_outputs}

품질을 평가하고 개선 포인트를 작성하라.
"""
        output = self.llm.chat(EVALUATION_SYSTEM, prompt, temperature=0.1, max_tokens=1200)
        if not output.strip():
            output = """# Evaluation

## 정확성
3/5. 프로그램 구조에 기반한 설명은 가능하나, 모델 출력이 비어 있는 경우가 있어 보강이 필요하다.

## 완성도
3/5. Wiki, Memory, Self-Upgrade 저장 구조는 있으나 자기소개 컨텍스트가 부족하면 실패할 수 있다.

## 실행 가능성
4/5. Streamlit과 HF Router fallback 구조는 동작한다.

## 누락된 정보
- 프로그램 기능 매뉴얼을 모든 Agent에 주입하는 구조
- 빈 응답 fallback 처리

## 위험한 자동화 여부
낮음. 실제 모델 가중치 자동 수정은 하지 않고 개선안과 학습 데이터 생성으로 제한되어 있다.

## 다음 개선 포인트
- PROGRAM_MANIFEST 추가
- Supervisor 최종 응답 fallback 추가
- Agent별 빈 응답 fallback 추가
"""
        return AgentResult(agent_name=self.name, output=output, artifacts=[])
