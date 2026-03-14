"""
Agent-MAC entrypoint.

Usage:
  python main.py                          # Interactive REPL
  python main.py "your query here"        # Single query
  python main.py --demo                   # Run capability demo
"""
from __future__ import annotations

import asyncio
import sys

from rich.console import Console

from agent import SelfProgrammingAgent
from core.config import AgentConfig

console = Console()


async def run_demo(agent: SelfProgrammingAgent) -> None:
    """
    Demonstrates the self-programming capability:

    1. Ask the agent to do something that requires a non-existent tool
    2. Watch it synthesize the tool and use it
    3. Observe reflection and memory storage
    """
    demos = [
        "What tools do you currently have available?",
        (
            "I need you to create a tool that can calculate the Fibonacci sequence "
            "up to N numbers, then use it to get the first 10 Fibonacci numbers."
        ),
        (
            "Store in memory that my preferred programming language is Python "
            "and I prefer concise code. Then recall it to confirm."
        ),
        "What tools do you have now? How many did you synthesize this session?",
    ]

    for i, query in enumerate(demos, 1):
        console.print(f"\n[bold]Demo {i}/{len(demos)}[/bold]")
        result = await agent.query(query)
        console.print(f"\n[green]Result:[/green] {result[:400]}\n")
        console.print("─" * 60)


async def main() -> None:
    config = AgentConfig()
    agent = SelfProgrammingAgent(config)
    await agent.initialize()

    args = sys.argv[1:]

    if "--demo" in args:
        await run_demo(agent)
    elif args and not args[0].startswith("--"):
        # Single query mode
        query = " ".join(args)
        result = await agent.query(query)
        console.print(f"\n[green]Result:[/green] {result}")
    else:
        # Interactive mode
        await agent.interactive_loop()


if __name__ == "__main__":
    asyncio.run(main())
