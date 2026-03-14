"""
Agent — top-level orchestrator.

Wires together all components:
  Gateway ← SkillsRegistry ← [builtin + dynamic skills]
  AgentRuntime → Gateway (dispatch)
  MetaProgrammer → Gateway (register new tools)
  Reflector → EpisodicMemory (learn from sessions)
  SemanticMemory → AgentRuntime (context injection)

The self-programming loop:
  query → Runtime → [tool use] → Gateway
                       ↓
                  Gap detected
                       ↓
               MetaProgrammer.synthesize()
                       ↓
                  New tool registered
                       ↓
              Runtime continues with new tool
                       ↓
                  Task completed
                       ↓
                  Reflector.reflect()
                       ↓
              EpisodicMemory.record()
                       ↓
              (next session is smarter)
"""
from __future__ import annotations

import asyncio
import json
from typing import Any

import anthropic
from rich.console import Console
from rich.rule import Rule

from core.config import AgentConfig
from core.gateway import Gateway
from core.runtime import AgentRuntime
from memory.episodic import EpisodicMemory
from memory.semantic import SemanticMemory
from meta.programmer import MetaProgrammer
from meta.reflector import Reflector
from skills.registry import SkillsRegistry

console = Console()


class SelfProgrammingAgent:
    """
    The self-programming agent.

    Combines all components into a cohesive system that:
    1. Executes tasks with a rich tool set
    2. Detects capability gaps
    3. Synthesizes new Python tools at runtime
    4. Reflects on and learns from each session
    5. Gets smarter over time via memory and synthesis
    """

    def __init__(self, config: AgentConfig | None = None) -> None:
        self.config = config or AgentConfig()
        self.client = anthropic.AsyncAnthropic(api_key=self.config.api_key)

        # Core components
        self.gateway = Gateway(self.config)
        self.runtime = AgentRuntime(self.config, self.gateway, self.client)

        # Memory systems
        self.episodic = EpisodicMemory(self.config.memory_dir)
        self.semantic = SemanticMemory(self.config.memory_dir)

        # Meta-programming
        self.programmer = MetaProgrammer(self.config, self.gateway, self.client)
        self.reflector = Reflector(self.config, self.client)

        # Skills
        self.registry = SkillsRegistry(self.config, self.gateway)

        self._synthesized_this_session: list[str] = []

    async def initialize(self) -> None:
        """Bootstrap the agent: load skills, wire dynamic handlers."""
        console.print(Rule("[bold cyan]Agent-MAC: Self-Programming Agent[/bold cyan]"))
        console.print("[dim]Initializing components...[/dim]\n")

        # Load all skills from disk
        count = self.registry.discover_and_load()
        console.print(f"[green]✓[/green] Loaded [bold]{count}[/bold] skills\n")

        # Wire up special tool handlers that need agent context

        # 1. request_skill_synthesis — calls MetaProgrammer
        async def synthesis_handler(params: dict) -> str:
            result = await self.programmer.synthesize_and_register(
                capability_description=params["capability"],
                examples=params.get("examples", []),
            )
            if result.get("success"):
                tool_name = result["tool_name"]
                self._synthesized_this_session.append(tool_name)
                # Reload registry to pick up any file-system changes
                self.registry.reload_dynamic()
                return (
                    f"✓ New tool '{tool_name}' synthesized and registered!\n"
                    f"Description: {result['description']}\n"
                    f"You can now use it directly."
                )
            return f"✗ Synthesis failed: {result.get('error', 'Unknown error')}"

        self.gateway.register_tool(
            name="request_skill_synthesis",
            handler=synthesis_handler,
            schema={
                "name": "request_skill_synthesis",
                "description": (
                    "Request the creation of a new tool/skill that doesn't currently exist. "
                    "The system will synthesize Python code for the capability and register "
                    "it immediately so you can use it in this session."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "capability": {
                            "type": "string",
                            "description": "Natural language description of the capability needed",
                        },
                        "examples": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Example use cases",
                        },
                    },
                    "required": ["capability"],
                },
            },
        )

        # 2. list_tools — shows all registered tools
        async def list_tools_handler(params: dict) -> str:
            tools = self.gateway.tool_list
            filt = params.get("filter", "").lower()
            if filt:
                tools = [t for t in tools if filt in t["name"].lower()]
            names = [t["name"] for t in tools]
            return f"{len(names)} tools available:\n" + "\n".join(f"  • {n}" for n in sorted(names))

        self.gateway.register_tool(
            name="list_tools",
            handler=list_tools_handler,
            schema={
                "name": "list_tools",
                "description": "List all currently available tools/skills",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "filter": {"type": "string", "description": "Substring filter"}
                    },
                    "required": [],
                },
            },
        )

        # 3. memory_store / memory_recall — connected to SemanticMemory
        async def memory_store_handler(params: dict) -> str:
            self.semantic.store(
                key=params["key"],
                value=params["value"],
                category=params.get("category", "fact"),
            )
            return f"Stored '{params['key']}'"

        async def memory_recall_handler(params: dict) -> str:
            key = params.get("key", "")
            if key:
                val = self.semantic.recall(key)
                return val or f"No memory for '{key}'"
            category = params.get("category", "")
            if category:
                entries = self.semantic.get_by_category(category)
                return json.dumps(entries, indent=2) if entries else f"No entries in '{category}'"
            return self.semantic.get_context_summary()

        self.gateway.register_tool(
            "memory_store", memory_store_handler,
            {
                "name": "memory_store",
                "description": "Store a fact in persistent semantic memory",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string"},
                        "value": {"type": "string"},
                        "category": {"type": "string"},
                    },
                    "required": ["key", "value"],
                },
            },
        )
        self.gateway.register_tool(
            "memory_recall", memory_recall_handler,
            {
                "name": "memory_recall",
                "description": "Recall facts from persistent semantic memory",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string"},
                        "category": {"type": "string"},
                    },
                    "required": [],
                },
            },
        )

        # Show memory summary
        mem_summary = self.episodic.summary()
        if mem_summary.get("total_episodes", 0) > 0:
            console.print(f"[dim]Memory: {mem_summary['total_episodes']} past episodes, "
                          f"avg effectiveness {mem_summary['avg_effectiveness']}[/dim]")

    async def query(self, prompt: str) -> str:
        """
        Execute a query through the full self-programming agent pipeline.

        1. Retrieve relevant memory context
        2. Run the agentic loop
        3. Reflect and learn
        4. Record the episode
        """
        # Step 1: Memory-augmented context
        episodic_context = self.episodic.get_context_for_task(prompt)
        semantic_context = self.semantic.get_context_summary(max_entries=5)
        extra_context = "\n\n".join(filter(None, [episodic_context, semantic_context]))

        # Step 2: Execute
        session = self.gateway.new_session()
        result = await self.runtime.run(prompt, session, extra_context)

        # Step 3: Reflect
        reflection = await self.reflector.reflect(session, prompt, result)

        # Step 4: Record episode
        self.episodic.record(
            task=prompt,
            result=result,
            tools_used=[tc["name"] for tc in session.tool_calls],
            gaps=session.capability_gaps,
            skills_synthesized=self._synthesized_this_session[:],
            lessons=reflection.get("lessons", []),
            effectiveness=reflection.get("effectiveness_score", 0.8),
            turns=session.turn_count,
        )

        # Step 5: Auto-synthesize high-priority suggested skills
        if self.config.auto_synthesize:
            for skill_suggestion in reflection.get("suggested_skills", []):
                if skill_suggestion.get("priority") == "high":
                    if not self.gateway.has_tool(skill_suggestion["name"]):
                        await self.programmer.synthesize_and_register(
                            capability_description=skill_suggestion["description"],
                        )
                        self._synthesized_this_session.append(skill_suggestion["name"])

        return result

    async def interactive_loop(self) -> None:
        """Run an interactive REPL for the agent."""
        await self.initialize()
        console.print(Rule())
        console.print("[bold green]Agent ready. Type your query (or 'quit' to exit).[/bold green]\n")

        while True:
            try:
                prompt = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if not prompt:
                continue
            if prompt.lower() in ("quit", "exit", "q"):
                break

            result = await self.query(prompt)
            console.print(f"\n[bold green]Agent:[/bold green] {result}\n")
            console.print(Rule())
