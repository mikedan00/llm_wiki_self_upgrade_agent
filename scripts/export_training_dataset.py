from pathlib import Path

src = Path("data/training/sft_dataset.jsonl")
dst = Path("data/training/export_sft_dataset.jsonl")
dst.parent.mkdir(parents=True, exist_ok=True)

if not src.exists():
    print("학습 데이터가 없습니다. 먼저 앱에서 작업을 실행하세요.")
else:
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Exported: {dst}")
