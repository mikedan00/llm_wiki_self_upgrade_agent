from datetime import datetime
import json
from src.core.config import Settings

class Storage:
    def __init__(self, settings: Settings):
        self.root = settings.data_path
        for name in ["sources", "wiki", "memory", "runs", "upgrades", "training"]:
            (self.root / name).mkdir(parents=True, exist_ok=True)

    def timestamp(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def write_text(self, area: str, filename: str, content: str):
        path = self.root / area / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def append_text(self, area: str, filename: str, content: str):
        path = self.root / area / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(content)
        return path

    def write_json(self, area: str, filename: str, obj):
        path = self.root / area / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def read_json_relative(self, rel_path: str):
        path = self.root / rel_path
        return json.loads(path.read_text(encoding="utf-8"))

    def read_relative(self, rel_path: str) -> str:
        path = self.root / rel_path
        return path.read_text(encoding="utf-8")

    def list_files(self, area: str, suffix: str = "") -> list[str]:
        root = self.root / area
        if not root.exists():
            return []
        files = []
        for p in sorted(root.rglob(f"*{suffix}"), reverse=True):
            if p.is_file():
                files.append(str(p.relative_to(self.root)))
        return files

    def collect_context(self, max_chars: int = 12000) -> str:
        chunks = []
        for area in ["wiki", "memory"]:
            for rel in self.list_files(area, suffix=".md")[:20]:
                text = self.read_relative(rel)
                chunks.append(f"\n\n--- FILE: {rel} ---\n{text[:2000]}")
        combined = "".join(chunks)
        return combined[:max_chars]
