"""Validate the knowledge base: valid JSON, required fields, duplicate questions."""
import json
from collections import defaultdict
from pathlib import Path

problems, seen, total = [], defaultdict(list), 0
for path in sorted(Path("data").glob("*.json")):
    try:
        entries = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        problems.append(f"{path.name}: invalid JSON ({e})")
        continue
    for i, e in enumerate(entries, 1):
        where = f"{path.name} entry {i}"
        if not all(k in e for k in ("category", "questions", "answer")):
            problems.append(f"{where}: needs category, questions and answer")
            continue
        if len(e["questions"]) < 3:
            problems.append(f"{where}: add at least 3 question phrasings")
        for q in e["questions"]:
            total += 1
            seen[q.strip().lower()].append(where)
for q, places in seen.items():
    if len(places) > 1:
        problems.append(f"duplicate question {q!r} in: {', '.join(places)}")
print(f"{total} question phrasings checked")
print("All good" if not problems else "\n".join(problems))