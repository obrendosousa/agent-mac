"""
Agent Runtime — the execution engine.

Implements the agentic loop:
  1. Send prompt + tools to Claude
  2. Claude responds with tool_use blocks
  3. Dispatch tools via Gateway
  4. Feed results back
  5. Repeat until end_turn or max_iterations
  6. After completion, trigger reflection
"""
from __future__ import annotations

import json
from typing import Any

import anthropic
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from core.config import AgentConfig
from core.gateway import Gateway, Session

console = Console()

SYSTEM_PROMPT = """You are an advanced autonomous AI agent with self-programming capabilities.

You can:
- Use registered tools to accomplish tasks
- Analyze your own capability gaps and request new tool synthesis
- Learn from past interactions via memory tools
- Collaborate with sub-agents for parallelizable work

When you realize you need a capability that doesn't exist as a tool:
1. Use the `request_skill_synthesis` tool to describe what you need
2. The system will generate and register a new tool dynamically
3. Then proceed with the task using the newly available tool

Always be explicit about what you are doing and why. When stuck, reflect on
what tool or information would unblock you.
"""


class AgentRuntime:
    """
    Core execution loop for the agent.

    Drives the conversation with Claude, dispatching tool calls
    through the Gateway and accumulating results.
    """

    def __init__(
        self,
        config: AgentConfig,
        gateway: Gateway,
        anthropic_client: anthropic.AsyncAnthropic,
    ) -> None:
        self.config = config
        self.gateway = gateway
        self.client = anthropic_client
        self._system_prompt = SYSTEM_PROMPT

    def update_system_prompt(self, new_prompt: str) -> None:
        """Allow meta-programming to evolve the system prompt."""
        self._system_prompt = new_prompt
        console.print("[bold cyan]★ System prompt updated by meta-programming engine[/bold cyan]")

    async def run(
        self,
        prompt: str,
        session: Session,
        extra_context: str = "",
    ) -> str:
        """
        Execute a query through the full agentic loop.
        Returns the final text response.
        """
        system = self._system_prompt
        if extra_context:
            system += f"\n\n## Context from Memory\n{extra_context}"

        messages: list[dict[str, Any]] = [
            {"role": "user", "content": prompt}
        ]

        console.print(Panel(f"[bold]Query:[/bold] {prompt[:120]}...", title="[cyan]Agent Runtime[/cyan]"))

        for iteration in range(self.config.max_iterations):
            session.turn_count += 1

            # Build API call params
            params: dict[str, Any] = {
                "model": self.config.model,
                "max_tokens": 8096,
                "system": system,
                "messages": messages,
                "tools": self.gateway.tool_list,
            }
            if self.config.thinking:
                params["thinking"] = {"type": "adaptive"}

            console.print(f"[dim]→ API call #{iteration + 1} ({len(self.gateway.tool_list)} tools available)[/dim]")

            # Stream for responsiveness
            async with self.client.messages.stream(**params) as stream:
                response = await stream.get_final_message()

            # Check stop reason
            if response.stop_reason == "end_turn":
                final_text = self._extract_text(response)
                console.print(f"\n[green]✓ Done in {iteration + 1} iteration(s)[/green]")
                return final_text

            if response.stop_reason != "tool_use":
                console.print(f"[yellow]Unexpected stop reason: {response.stop_reason}[/yellow]")
                return self._extract_text(response)

            # Process tool calls
            tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for tool_block in tool_use_blocks:
                result = await self._execute_tool(tool_block, session)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": json.dumps(result) if not isinstance(result, str) else result,
                })

            messages.append({"role": "user", "content": tool_results})

        console.print(f"[red]Max iterations ({self.config.max_iterations}) reached[/red]")
        return self._extract_text(response) if 'response' in dir() else "Max iterations reached without completion."

    async def _execute_tool(
        self,
        tool_block: Any,
        session: Session,
    ) -> Any:
        """Dispatch a single tool call and return its result."""
        name = tool_block.name
        inp = dict(tool_block.input)

        console.print(f"  [bold blue]⚙ Tool:[/bold blue] [cyan]{name}[/cyan]")
        if inp:
            preview = json.dumps(inp, indent=2)[:200]
            console.print(Syntax(preview, "json", theme="monokai"))

        try:
            result = await self.gateway.dispatch(name, inp, session)
            console.print(f"  [green]✓ Result:[/green] {str(result)[:150]}")
            return result
        except KeyError as e:
            # Tool not found — record as capability gap
            gap = f"Missing tool: {name} — {str(e)}"
            session.record_gap(f"Tool '{name}' not available: {inp}")
            return {"error": str(e), "hint": "Use request_skill_synthesis to create this tool"}
        except Exception as e:
            console.print(f"  [red]✗ Error:[/red] {e}")
            return {"error": str(e)}

    @staticmethod
    def _extract_text(response: Any) -> str:
        parts = []
        for block in response.content:
            if block.type == "text":
                parts.append(block.text)
        return "\n".join(parts) if parts else ""
