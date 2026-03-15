"""
Agent-MAC entrypoint.

Uso:
  python main.py                    # REPL interativo (Agent SDK)
  python main.py "sua query"        # Query única
  python main.py --demo             # Demo de auto-programação
  python main.py --legacy           # Usa implementação original (sem Agent SDK)

Para modo servidor 24/7:
  python server.py api --port 8080
  python server.py schedule --interval 3600 --task "..."
  python server.py watch --path ./src --task "Arquivos alterados: {files}"
"""
from __future__ import annotations

import asyncio
import sys

from rich.console import Console
from rich.rule import Rule

from core.config import AgentConfig

console = Console()


async def run_demo(agent) -> None:
    demos = [
        "Liste as ferramentas disponíveis para você.",
        (
            "Preciso de um tool que calcule números primos até N. "
            "Sintetize-o e depois use para listar os primeiros 10 primos."
        ),
        "Guarde na memória que minha linguagem preferida é Python. Depois confirme o que foi guardado.",
        "Que skills você sintetizou nessa sessão? Mostre o histórico da memória.",
    ]
    for i, query in enumerate(demos, 1):
        console.print(Rule(f"[bold]Demo {i}/{len(demos)}[/bold]"))
        result = await agent.query(query)
        console.print(f"[green]Resultado:[/green] {result[:500]}\n")


async def main() -> None:
    args = sys.argv[1:]
    config = AgentConfig()

    if "--legacy" in args:
        # Implementação original sem Agent SDK
        from agent import SelfProgrammingAgent
        agent = SelfProgrammingAgent(config)
        await agent.initialize()
    else:
        # Nova implementação com Agent SDK
        from agent_sdk import AgentMacSDK
        agent = AgentMacSDK(config)

    if "--demo" in args:
        await run_demo(agent)
    elif args and not args[0].startswith("--"):
        result = await agent.query(" ".join(a for a in args if not a.startswith("--")))
        console.print(f"\n[green]Resultado:[/green] {result}")
    else:
        await agent.interactive_loop()


if __name__ == "__main__":
    asyncio.run(main())
