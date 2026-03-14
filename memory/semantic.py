"""
Semantic Memory — stores learned facts, solutions, and preferences.

Unlike episodic memory (what happened), semantic memory stores
what the agent knows: facts, solutions to recurring problems,
user preferences, discovered patterns.

Used to inject relevant context into new queries.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


class SemanticMemory:
    """
    Key-value store for facts and knowledge.

    Backed by a simple JSON file. Each entry has:
    - value: the stored information
    - category: 'fact' | 'preference' | 'solution' | 'lesson'
    - access_count: how often it's been retrieved (for importance ranking)
    - created_at: timestamp
    """

    def __init__(self, memory_dir: str = ".memory") -> None:
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        self._path = self.memory_dir / "semantic.json"
        self._data: dict[str, dict] = self._load()

    def _load(self) -> dict[str, dict]:
        if not self._path.exists():
            return {}
        try:
            return json.loads(self._path.read_text())
        except Exception:
            return {}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2))

    def store(self, key: str, value: str, category: str = "fact") -> None:
        self._data[key] = {
            "value": value,
            "category": category,
            "access_count": 0,
            "created_at": time.time(),
        }
        self._save()

    def recall(self, key: str) -> str | None:
        entry = self._data.get(key)
        if entry:
            entry["access_count"] = entry.get("access_count", 0) + 1
            self._save()
            return entry["value"]
        return None

    def get_by_category(self, category: str) -> dict[str, str]:
        return {
            k: v["value"]
            for k, v in self._data.items()
            if v.get("category") == category
        }

    def get_all(self) -> dict[str, Any]:
        return dict(self._data)

    def get_context_summary(self, max_entries: int = 10) -> str:
        """Return most-accessed facts as a context string."""
        if not self._data:
            return ""
        sorted_entries = sorted(
            self._data.items(),
            key=lambda x: x[1].get("access_count", 0),
            reverse=True,
        )
        parts = ["Known facts and preferences:"]
        for key, entry in sorted_entries[:max_entries]:
            parts.append(f"- {key}: {entry['value']}")
        return "\n".join(parts)
