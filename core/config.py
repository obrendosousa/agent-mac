"""Agent configuration."""
from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class AgentConfig:
    # Model used for main reasoning
    model: str = "claude-opus-4-6"
    # Model used for fast/cheap operations (skill eval, summaries)
    fast_model: str = "claude-haiku-4-5"
    # Max tool loop iterations per query
    max_iterations: int = 20
    # Enable adaptive thinking for complex tasks
    thinking: bool = True
    # Directory where dynamic skills are stored
    skills_dir: str = "skills/dynamic"
    # Directory where memory is persisted
    memory_dir: str = ".memory"
    # Whether to auto-synthesize new skills after failures
    auto_synthesize: bool = True
    # Max skills to load per session
    max_skills: int = 50
    # API key (from env by default)
    api_key: str = field(default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY", ""))

    def __post_init__(self) -> None:
        os.makedirs(self.skills_dir, exist_ok=True)
        os.makedirs(self.memory_dir, exist_ok=True)
