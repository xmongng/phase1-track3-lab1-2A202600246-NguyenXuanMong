from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Iterable
from .schemas import QAExample, RunRecord

def normalize_answer(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text

def load_dataset(path: str | Path) -> list[QAExample]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    
    if raw and "qid" in raw[0]:
        return [QAExample.model_validate(item) for item in raw]
        
    examples = []
    for item in raw:
        context_chunks = [{"title": t, "text": " ".join(s)} for t, s in item.get("context", [])]
        example = QAExample(
            qid=item.get("_id", ""),
            difficulty=item.get("level", "medium"),
            question=item.get("question", ""),
            gold_answer=item.get("answer", ""),
            context=context_chunks
        )
        examples.append(example)
    return examples

def save_jsonl(path: str | Path, records: Iterable[RunRecord]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(record.model_dump_json() + "\n")
