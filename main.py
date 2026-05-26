import argparse
from src.core.config import get_settings
from src.agents.supervisor import SupervisorAgent

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True, help="Agent에게 수행시킬 작업")
    parser.add_argument("--source", default="", help="추가 원본 텍스트")
    args = parser.parse_args()

    settings = get_settings()
    supervisor = SupervisorAgent(settings)
    result = supervisor.run(task=args.task, source_text=args.source)

    print("\n=== FINAL ANSWER ===\n")
    print(result.final_answer)
    print("\n=== RUN ID ===")
    print(result.run_id)

if __name__ == "__main__":
    main()
