"""
Agent-MAC v2: Agent SDK Edition

Usa o claude_agent_sdk como base — ganha todos os tools nativos do Claude Code
(Read, Edit, Write, Bash, Glob, Grep, WebSearch, WebFetch, Agent)
e expõe os tools customizados (MetaProgrammer, Memory) via MCP server embutido.

Arquitetura:
  Agent SDK (agentic loop nativo)
       ↓
  MCP Server (tools customizados em-processo)
    ├─ request_skill_synthesis  → MetaProgrammer
    ├─ memory_store/recall       → SemanticMemory
    ├─ reflect                   → Reflector
    └─ list_synthesized_skills   → SkillsRegistry
"""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

import anthropic
from claude_agent_sdk import (
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    SystemMessage,
    tool,
    create_sdk_mcp_server,
)
from rich.console import Console
from rich.rule import Rule

from core.config import AgentConfig
from memory.episodic import EpisodicMemory
from memory.semantic import SemanticMemory
from meta.programmer import MetaProgrammer
from meta.reflector import Reflector

console = Console()


def build_mcp_server(
    config: AgentConfig,
    programmer: MetaProgrammer,
    reflector: Reflector,
    semantic: SemanticMemory,
    episodic: EpisodicMemory,
    synthesized_skills: list[str],
):
    """
    Cria um MCP server em-processo com os tools customizados do agent-mac.
    Esses tools ficam disponíveis para o Agent SDK junto com os tools nativos.
    """

    # ── Tool: request_skill_synthesis ────────────────────────────────────────
    @tool(
        "request_skill_synthesis",
        "Synthesize and register a new Python tool at runtime when a needed capability is missing",
        {
            "capability": str,
            "examples": list,
        },
    )
    async def request_skill_synthesis(args: dict):
        capability = args.get("capability", "")
        examples = args.get("examples", [])
        result = await programmer.synthesize_and_register(capability, examples)
        if result.get("success"):
            synthesized_skills.append(result["tool_name"])
            text = (
                f"✓ Tool '{result['tool_name']}' synthesized!\n"
                f"Description: {result['description']}\n"
                f"File: {result.get('file', '')}\n"
                f"Note: this tool runs as a standalone Python function. "
                f"Use 'list_synthesized_skills' to see all available synthesized tools."
            )
        else:
            text = f"✗ Synthesis failed: {result.get('error')}"
        return {"content": [{"type": "text", "text": text}]}

    # ── Tool: run_synthesized_skill ───────────────────────────────────────────
    @tool(
        "run_synthesized_skill",
        "Execute a previously synthesized skill by name with given parameters",
        {
            "skill_name": str,
            "params": dict,
        },
    )
    async def run_synthesized_skill(args: dict):
        import importlib.util, sys
        skill_name = args.get("skill_name", "")
        params = args.get("params", {})
        skill_path = Path(config.skills_dir) / f"{skill_name}.py"
        if not skill_path.exists():
            return {"content": [{"type": "text", "text": f"Skill '{skill_name}' not found in {config.skills_dir}"}]}
        try:
            spec = importlib.util.spec_from_file_location(f"_skill_{skill_name}", skill_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[f"_skill_{skill_name}"] = module
            spec.loader.exec_module(module)
            result = await module.run(params)
            return {"content": [{"type": "text", "text": str(result)}]}
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Error running skill: {e}"}]}

    # ── Tool: list_synthesized_skills ─────────────────────────────────────────
    @tool(
        "list_synthesized_skills",
        "List all dynamically synthesized skills available to run",
        {},
    )
    async def list_synthesized_skills(args: dict):
        dynamic_dir = Path(config.skills_dir)
        skills = []
        for f in sorted(dynamic_dir.glob("*.py")):
            if f.name.startswith("_"):
                continue
            try:
                content = f.read_text()
                name_line = next((l for l in content.splitlines() if l.startswith('NAME')), '')
                desc_line = next((l for l in content.splitlines() if l.startswith('DESCRIPTION')), '')
                name = name_line.split('=')[1].strip().strip('"') if '=' in name_line else f.stem
                desc = desc_line.split('=')[1].strip().strip('"') if '=' in desc_line else ""
                skills.append(f"• {name}: {desc}")
            except Exception:
                skills.append(f"• {f.stem}")
        text = f"{len(skills)} synthesized skills:\n" + "\n".join(skills) if skills else "No synthesized skills yet."
        return {"content": [{"type": "text", "text": text}]}

    # ── Tool: memory_store ────────────────────────────────────────────────────
    @tool(
        "memory_store",
        "Store a fact, preference, or lesson in persistent semantic memory",
        {
            "key": str,
            "value": str,
            "category": str,
        },
    )
    async def memory_store(args: dict):
        semantic.store(args["key"], args["value"], args.get("category", "fact"))
        return {"content": [{"type": "text", "text": f"Stored: '{args['key']}'"}]}

    # ── Tool: memory_recall ───────────────────────────────────────────────────
    @tool(
        "memory_recall",
        "Recall facts from persistent semantic memory",
        {
            "key": str,
            "category": str,
        },
    )
    async def memory_recall(args: dict):
        key = args.get("key", "")
        if key:
            val = semantic.recall(key) or f"No memory for '{key}'"
            return {"content": [{"type": "text", "text": val}]}
        category = args.get("category", "")
        if category:
            entries = semantic.get_by_category(category)
            text = json.dumps(entries, indent=2) if entries else f"No entries in '{category}'"
        else:
            text = semantic.get_context_summary()
        return {"content": [{"type": "text", "text": text}]}

    # ── Tool: session_history ─────────────────────────────────────────────────
    @tool(
        "session_history",
        "Show summary of past sessions and lessons learned from episodic memory",
        {"last_n": int},
    )
    async def session_history(args: dict):
        summary = episodic.summary()
        text = json.dumps(summary, indent=2)
        return {"content": [{"type": "text", "text": text}]}

    # ── Tool: connect_to_pc ────────────────────────────────────────────────────
    @tool(
        "connect_to_pc",
        "Connect to a remote Agent-MAC server running on your PC to send queries, check health, or list skills",
        {
            "action": str,
            "host": str,
            "port": int,
            "prompt": str,
            "auth_token": str,
            "timeout": int,
        },
    )
    async def connect_to_pc(args: dict):
        from skills.builtin.connect_to_pc import run as pc_run
        result = await pc_run(args)
        return {"content": [{"type": "text", "text": result}]}

    return create_sdk_mcp_server(
        "agent-mac-tools",
        tools=[
            request_skill_synthesis,
            run_synthesized_skill,
            list_synthesized_skills,
            memory_store,
            memory_recall,
            session_history,
            connect_to_pc,
        ],
    )


class AgentMacSDK:
    """
    Agent-MAC usando o Agent SDK como base.

    Ganha gratuitamente: Read, Edit, Write, Bash, Glob, Grep,
    WebSearch, WebFetch, AskUserQuestion, Agent (subagents)

    Adiciona via MCP: síntese de skills, memória, reflexão.
    """

    SYSTEM_PROMPT = """\
Você é um agente autônomo com capacidade de auto-programação.

Ferramentas nativas disponíveis: Read, Edit, Write, Bash, Glob, Grep, WebSearch, WebFetch, Agent.

Ferramentas customizadas disponíveis via MCP:
- request_skill_synthesis: quando precisar de uma capacidade que não existe, sintetize um novo tool Python
- run_synthesized_skill: execute um skill sintetizado pelo nome
- list_synthesized_skills: liste os skills disponíveis
- memory_store/recall: persista e recupere fatos entre sessões
- session_history: veja o histórico de sessões passadas
- connect_to_pc: conecte-se a um servidor Agent-MAC remoto no seu PC para enviar queries e gerenciar skills

Fluxo de auto-programação:
1. Detectou que falta uma capacidade? → chame request_skill_synthesis
2. Skill será sintetizado em Python e salvo em skills/dynamic/
3. Execute com run_synthesized_skill para usar imediatamente
4. Na próxima sessão o skill já está disponível

Seja proativo: use memória para guardar preferências e lições aprendidas.
"""

    def __init__(self, config: AgentConfig | None = None) -> None:
        self.config = config or AgentConfig()
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=self.config.api_key)
        self.semantic = SemanticMemory(self.config.memory_dir)
        self.episodic = EpisodicMemory(self.config.memory_dir)
        self.programmer = MetaProgrammer(
            self.config,
            gateway=None,  # MetaProgrammer sem Gateway — salva em disco, usa run_synthesized_skill
            client=self.anthropic_client,
        )
        self.reflector = Reflector(self.config, self.anthropic_client)
        self._synthesized: list[str] = []
        self._mcp_server = build_mcp_server(
            self.config,
            self.programmer,
            self.reflector,
            self.semantic,
            self.episodic,
            self._synthesized,
        )

    def _build_options(self, extra_system: str = "") -> ClaudeAgentOptions:
        system = self.SYSTEM_PROMPT
        context = self.semantic.get_context_summary(max_entries=5)
        if context:
            system += f"\n\n## Memória semântica\n{context}"
        if extra_system:
            system += f"\n\n{extra_system}"

        return ClaudeAgentOptions(
            model=self.config.model,
            allowed_tools=[
                "Read", "Edit", "Write", "Bash",
                "Glob", "Grep", "WebSearch", "WebFetch",
                "AskUserQuestion", "Agent",
            ],
            mcp_servers={"agent-mac": self._mcp_server},
            system_prompt=system,
            max_turns=self.config.max_iterations,
            permission_mode="acceptEdits",
        )

    async def query(self, prompt: str) -> str:
        """Executa uma query completa com reflexão e memória."""
        options = self._build_options()
        result_text = ""
        session_id = None
        tool_calls: list[str] = []

        async with ClaudeSDKClient(options=options) as client:
            await client.query(prompt)
            async for message in client.receive_response():
                if isinstance(message, SystemMessage) and message.subtype == "init":
                    session_id = message.data.get("session_id")
                elif isinstance(message, ResultMessage):
                    result_text = message.result

        # Reflexão simplificada pós-tarefa
        from core.gateway import Session as FakeSession
        fake_session = FakeSession()
        fake_session.tool_calls = [{"name": t, "input": {}, "result": ""} for t in tool_calls]
        fake_session.capability_gaps = []
        reflection = await self.reflector.reflect(fake_session, prompt, result_text)

        self.episodic.record(
            task=prompt,
            result=result_text,
            tools_used=tool_calls,
            gaps=[],
            skills_synthesized=self._synthesized[:],
            lessons=reflection.get("lessons", []),
            effectiveness=reflection.get("effectiveness_score", 0.8),
            turns=0,
        )

        return result_text

    async def interactive_loop(self) -> None:
        """REPL interativo usando o Agent SDK."""
        console.print(Rule("[bold cyan]Agent-MAC v2 (Agent SDK)[/bold cyan]"))
        mem = self.episodic.summary()
        if mem.get("total_episodes", 0) > 0:
            console.print(f"[dim]{mem['total_episodes']} sessões passadas • "
                          f"effectiveness média: {mem['avg_effectiveness']}[/dim]")
        console.print("[bold green]Pronto. Digite sua query (ou 'sair').[/bold green]\n")

        options = self._build_options()

        while True:
            try:
                prompt = input("Você: ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not prompt or prompt.lower() in ("sair", "quit", "exit", "q"):
                break

            async with ClaudeSDKClient(options=options) as client:
                await client.query(prompt)
                async for message in client.receive_response():
                    if isinstance(message, ResultMessage):
                        console.print(f"\n[bold green]Agente:[/bold green] {message.result}\n")
                        console.print(Rule())
