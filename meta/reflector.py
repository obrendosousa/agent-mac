"""
Reflector — post-execution analysis engine.

After each task completes, the Reflector:
  1. Analyzes what tools were used and what gaps were hit
  2. Identifies patterns that could be turned into reusable skills
  3. Updates episodic memory with lessons learned
  4. (Optionally) proposes system prompt improvements

This is the "meta-learning" layer that makes the agent smarter over time.
"""
from __future__ import annotations

import json
from typing import Any

import anthropic
from rich.console import Console

from core.config import AgentConfig
from core.gateway import Session

console = Console()

REFLECTION_SYSTEM = """You are analyzing an AI agent's execution to extract learnings.

Given the session data (tool calls, gaps, results), produce a JSON reflection:
{
  "lessons": ["lesson 1", "lesson 2"],
  "suggested_skills": [
    {
      "name": "skill_name",
      "description": "what it should do",
      "priority": "high|medium|low",
      "reason": "why it would help"
    }
  ],
  "system_prompt_suggestion": "optional improvement to agent instructions",
  "effectiveness_score": 0.0-1.0
}
"""


class Reflector:
    """
    Analyzes completed sessions and extracts actionable improvements.

    This implements the "meta-learning loop" — the agent doesn't just
    execute tasks, it learns from them and evolves.
    """

    def __init__(
        self,
        config: AgentConfig,
        client: anthropic.AsyncAnthropic,
    ) -> None:
        self.config = config
        self.client = client

    async def reflect(
        self,
        session: Session,
        task: str,
        result: str,
    ) -> dict[str, Any]:
        """
        Perform post-task reflection.

        Returns structured insights including suggested skills to synthesize.
        """
        session_summary = {
            "task": task,
            "result_preview": result[:500],
            "turns": session.turn_count,
            "tools_used": [tc["name"] for tc in session.tool_calls],
            "tool_success_rate": self._compute_success_rate(session),
            "capability_gaps": session.capability_gaps,
        }

        console.print("[dim]🔍 Reflecting on session...[/dim]")

        try:
            response = await self.client.messages.create(
                model=self.config.fast_model,
                max_tokens=1024,
                system=REFLECTION_SYSTEM,
                messages=[{
                    "role": "user",
                    "content": f"Analyze this session:\n{json.dumps(session_summary, indent=2)}"
                }],
            )

            raw = next((b.text for b in response.content if b.type == "text"), "{}")
            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1].lstrip("json").strip()

            reflection = json.loads(raw)

            if reflection.get("lessons"):
                console.print(f"[cyan]💡 Lessons learned:[/cyan]")
                for lesson in reflection["lessons"][:3]:
                    console.print(f"   • {lesson}")

            if reflection.get("suggested_skills"):
                console.print(f"[yellow]🛠 Suggested new skills:[/yellow]")
                for skill in reflection["suggested_skills"][:3]:
                    console.print(f"   • [{skill['priority']}] {skill['name']}: {skill['description']}")

            return reflection

        except Exception as e:
            console.print(f"[dim]Reflection skipped: {e}[/dim]")
            return {}

    def _compute_success_rate(self, session: Session) -> float:
        if not session.tool_calls:
            return 1.0
        errors = sum(
            1 for tc in session.tool_calls
            if isinstance(tc.get("result"), dict) and "error" in tc["result"]
        )
        return 1.0 - (errors / len(session.tool_calls))
