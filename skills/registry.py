"""
Skills Registry — discovers, loads, and manages all skills.

Skill discovery order (highest precedence first):
  1. Dynamic skills (synthesized at runtime)   → skills/dynamic/*.py
  2. User skills (custom user additions)        → skills/user/*.py
  3. Built-in skills (shipped with agent)       → skills/builtin/*.py

Each skill file must define:
  - NAME: str
  - DESCRIPTION: str
  - PARAMETERS: dict  (JSON Schema)
  - async def run(params: dict) -> str
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

from rich.console import Console

from core.config import AgentConfig
from core.gateway import Gateway

console = Console()

# Directories to scan (in precedence order)
SKILL_DIRS = ["skills/dynamic", "skills/user", "skills/builtin"]


class SkillsRegistry:
    """
    Auto-discovers and loads skill files, registering them with the Gateway.

    This mirrors OpenClaw's ClawHub but with dynamic loading — skills
    synthesized at runtime are immediately available.
    """

    def __init__(self, config: AgentConfig, gateway: Gateway) -> None:
        self.config = config
        self.gateway = gateway
        self._loaded: dict[str, Path] = {}

    def discover_and_load(self) -> int:
        """
        Scan all skill directories and load found skills.
        Returns the count of newly loaded skills.
        """
        count = 0
        for dir_name in SKILL_DIRS:
            skill_dir = Path(dir_name)
            if not skill_dir.exists():
                continue
            for skill_file in sorted(skill_dir.glob("*.py")):
                if skill_file.name.startswith("_"):
                    continue
                if skill_file.stem in self._loaded:
                    continue  # Already loaded
                if self._load_skill(skill_file):
                    count += 1
        return count

    def reload_dynamic(self) -> int:
        """
        Reload only dynamic skills — called after new skill synthesis.
        Returns count of newly loaded skills.
        """
        dynamic_dir = Path(self.config.skills_dir)
        count = 0
        for skill_file in sorted(dynamic_dir.glob("*.py")):
            if skill_file.name.startswith("_"):
                continue
            # Force reload if already loaded (skill may have been updated)
            if self._load_skill(skill_file, force=True):
                count += 1
        return count

    def _load_skill(self, path: Path, force: bool = False) -> bool:
        """Load a single skill file and register it."""
        skill_name = path.stem
        if not force and self.gateway.has_tool(skill_name):
            return False

        try:
            module_name = f"_skill_{skill_name}"
            spec = importlib.util.spec_from_file_location(module_name, path)
            if spec is None or spec.loader is None:
                return False

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Validate required attributes
            for attr in ("NAME", "DESCRIPTION", "PARAMETERS", "run"):
                if not hasattr(module, attr):
                    console.print(f"[yellow]⚠ Skill {path.name} missing '{attr}', skipping[/yellow]")
                    return False

            tool_schema = {
                "name": module.NAME,
                "description": module.DESCRIPTION,
                "input_schema": module.PARAMETERS,
            }

            self.gateway.register_tool(
                name=module.NAME,
                handler=module.run,
                schema=tool_schema,
            )
            self._loaded[skill_name] = path
            return True

        except Exception as e:
            console.print(f"[red]✗ Failed to load skill {path.name}: {e}[/red]")
            return False

    def list_skills(self) -> list[dict[str, Any]]:
        """Return metadata for all loaded skills."""
        return [
            {"name": name, "file": str(path)}
            for name, path in self._loaded.items()
        ]
