"""
Gestor de trabajos vistos - evita enviar duplicados
"""
import json
import os
from typing import Set


class JobStorage:
    def __init__(self, filepath: str = "data/seen_jobs.json"):
        self.filepath = filepath
        self._seen: Set[str] = set()
        self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._seen = set(data.get("seen_ids", []))
            except Exception:
                self._seen = set()

    def _save(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump({"seen_ids": list(self._seen)}, f)

    def is_new(self, job_id: str) -> bool:
        return job_id not in self._seen

    def mark_seen(self, job_id: str):
        self._seen.add(job_id)
        self._save()

    def count(self) -> int:
        return len(self._seen)
