"""
Gateway — the single control plane for routing, sessions, and tool dispatch.

Like OpenClaw's Gateway, this is the nervous system of the agent.
All messages flow through here; it decides which runtime handles what.
"""
from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable

from rich.console import Console

from core.config import AgentConfig

console = Console()


@dataclass
class Session:
    """Represents an active agent session."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    created_at: float = field(default_factory=time.time)
    turn_count: int = 0
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    # Tracks capability gaps discovered during execution
    capability_gaps: list[str] = field(default_factory=list)

    def record_tool_call(self, name: str, input_data: dict, result: Any) -> None:
        self.tool_calls.append({
            "name": name,
            "input": input_data,
            "result": result,
            "turn": self.turn_count,
        })

    def record_gap(self, description: str) -> None:
        """Record a discovered capability gap for later synthesis."""
        if description not in self.capability_gaps:
            self.capability_gaps.append(description)
            console.print(f"[yellow]⚠ Capability gap detected:[/yellow] {description}")


# Type alias for tool handlers
ToolHandler = Callable[[dict[str, Any]], Awaitable[Any]]


class Gateway:
    """
    Central routing and control plane.

    Responsibilities:
    - Register / dispatch tools
    - Manage sessions
    - Route messages between components
    - Expose tool schemas to the LLM
    """

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self._tools: dict[str, ToolHandler] = {}
        self._tool_schemas: dict[str, dict] = {}
        self._sessions: dict[str, Session] = {}

    # ─── Tool Registry ───────────────────────────────────────────────────────

    def register_tool(
        self,
        name: str,
        handler: ToolHandler,
        schema: dict[str, Any],
    ) -> None:
        """Register a tool with its handler and JSON schema."""
        self._tools[name] = handler
        self._tool_schemas[name] = schema
        console.print(f"[dim]  ✓ tool registered: {name}[/dim]")

    def unregister_tool(self, name: str) -> None:
        self._tools.pop(name, None)
        self._tool_schemas.pop(name, None)

    @property
    def tool_list(self) -> list[dict[str, Any]]:
        """Returns all registered tools in Anthropic API format."""
        return list(self._tool_schemas.values())

    def has_tool(self, name: str) -> bool:
        return name in self._tools

    # ─── Tool Dispatch ────────────────────────────────────────────────────────

    async def dispatch(
        self,
        tool_name: str,
        tool_input: dict[str, Any],
        session: Session,
    ) -> Any:
        """Execute a tool and record the call in the session."""
        if tool_name not in self._tools:
            raise KeyError(f"Unknown tool: '{tool_name}'. Available: {list(self._tools)}")

        handler = self._tools[tool_name]
        result = await handler(tool_input)
        session.record_tool_call(tool_name, tool_input, result)
        return result

    # ─── Session Management ───────────────────────────────────────────────────

    def new_session(self) -> Session:
        session = Session()
        self._sessions[session.id] = session
        return session

    def get_session(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)
