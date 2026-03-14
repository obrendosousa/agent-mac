"""
Episodic Memory — stores the history of past sessions.

Each entry records:
- The task/query
- Tools used
- Outcome
- Lessons learned (from Reflector)
- Skills synthesized

This gives the agent a history of its own evolution.
"""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Episode:
    """A single completed task session."""
    task: str
    result_preview: str
    tools_used: list[str]
    gaps: list[str]
    skills_synthesized: list[str]
    lessons: list[str]
    effectiveness: float
    timestamp: float = field(default_factory=time.time)
    turns: int = 0


class EpisodicMemory:
    """
    Persists and retrieves past session episodes.

    Acts as the agent's long-term autobiographical memory —
    it can look back at what worked, what failed, and what it learned.
    """

    def __init__(self, memory_dir: str = ".memory") -> None:
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        self._path = self.memory_dir / "episodes.json"
        self._episodes: list[Episode] = self._load()

    def _load(self) -> list[Episode]:
        if not self._path.exists():
            return []
        try:
            raw = json.loads(self._path.read_text())
            return [Episode(**ep) for ep in raw]
        except Exception:
            return []

    def _save(self) -> None:
        data = [asdict(ep) for ep in self._episodes]
        self._path.write_text(json.dumps(data, indent=2))

    def record(
        self,
        task: str,
        result: str,
        tools_used: list[str],
        gaps: list[str],
        skills_synthesized: list[str],
        lessons: list[str],
        effectiveness: float,
        turns: int,
    ) -> Episode:
        episode = Episode(
            task=task,
            result_preview=result[:300],
            tools_used=tools_used,
            gaps=gaps,
            skills_synthesized=skills_synthesized,
            lessons=lessons,
            effectiveness=effectiveness,
            turns=turns,
        )
        self._episodes.append(episode)
        # Keep last 100 episodes
        self._episodes = self._episodes[-100:]
        self._save()
        return episode

    def get_context_for_task(self, task: str, max_episodes: int = 3) -> str:
        """
        Retrieve relevant past episodes as context for a new task.

        Simple keyword matching — could be upgraded to embeddings.
        """
        task_words = set(task.lower().split())
        relevant = []
        for ep in reversed(self._episodes):
            ep_words = set(ep.task.lower().split())
            overlap = len(task_words & ep_words)
            if overlap > 1:
                relevant.append((overlap, ep))

        relevant.sort(key=lambda x: -x[0])
        top = [ep for _, ep in relevant[:max_episodes]]

        if not top:
            return ""

        parts = ["Relevant past experiences:"]
        for ep in top:
            parts.append(
                f"- Task: {ep.task[:80]}\n"
                f"  Outcome: {ep.result_preview[:100]}\n"
                f"  Tools used: {', '.join(ep.tools_used[:5])}\n"
                f"  Lessons: {'; '.join(ep.lessons[:2])}"
            )
        return "\n".join(parts)

    def summary(self) -> dict[str, Any]:
        if not self._episodes:
            return {"total": 0}
        avg_effectiveness = sum(e.effectiveness for e in self._episodes) / len(self._episodes)
        all_lessons = [l for ep in self._episodes for l in ep.lessons]
        all_synth = [s for ep in self._episodes for s in ep.skills_synthesized]
        return {
            "total_episodes": len(self._episodes),
            "avg_effectiveness": round(avg_effectiveness, 2),
            "total_skills_synthesized": len(set(all_synth)),
            "top_lessons": list(set(all_lessons))[:5],
        }
