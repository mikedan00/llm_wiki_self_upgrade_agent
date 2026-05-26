import re

def slugify_kor(text: str, max_len: int = 60) -> str:
    text = re.sub(r"[\\/:*?\"<>|#]+", " ", text)
    text = re.sub(r"\s+", "_", text.strip())
    return text[:max_len] or "note"
