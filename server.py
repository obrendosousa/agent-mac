"""
Agent-MAC Server — modo daemon 24/7

Três modos de operação:
  1. watch   — monitora um diretório/arquivo e executa tasks ao detectar mudanças
  2. schedule — executa tasks em intervalo fixo (ex: a cada 30min)
  3. api      — servidor HTTP simples que aceita tasks via POST /query

Uso:
  python server.py watch --path ./src --task "Revise o código alterado e sugira melhorias"
  python server.py schedule --interval 3600 --task "Resuma as mudanças do dia no git"
  python server.py api --port 8080
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread

from rich.console import Console
from rich.rule import Rule

from agent_sdk import AgentMacSDK
from core.config import AgentConfig

console = Console()


# ─── Mode 1: File Watcher ─────────────────────────────────────────────────────

async def run_watch(agent: AgentMacSDK, watch_path: str, task_template: str, cooldown: int = 10) -> None:
    """Monitora alterações em arquivos e dispara o agente."""
    path = Path(watch_path)
    console.print(f"[cyan]👁 Watching:[/cyan] {path.resolve()}")
    console.print(f"[cyan]📋 Task:[/cyan] {task_template}\n")

    last_modified: dict[str, float] = {}

    def get_mtimes() -> dict[str, float]:
        if path.is_file():
            return {str(path): path.stat().st_mtime}
        return {
            str(f): f.stat().st_mtime
            for f in path.rglob("*")
            if f.is_file() and not any(p in str(f) for p in [".git", "__pycache__", ".memory"])
        }

    last_modified = get_mtimes()
    console.print("[dim]Baseline captured. Watching for changes...[/dim]")

    while True:
        await asyncio.sleep(2)
        current = get_mtimes()
        changed = [f for f, t in current.items() if last_modified.get(f) != t]
        new_files = [f for f in current if f not in last_modified]

        if changed or new_files:
            all_changed = changed + new_files
            console.print(Rule())
            console.print(f"[yellow]📝 Changed:[/yellow] {', '.join(Path(f).name for f in all_changed[:5])}")

            task = task_template.format(
                files="\n".join(all_changed),
                file_count=len(all_changed),
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            )

            result = await agent.query(task)
            console.print(f"[green]Result:[/green] {result[:300]}")
            last_modified = current
            await asyncio.sleep(cooldown)  # cooldown para não disparar em cascata


# ─── Mode 2: Scheduler ───────────────────────────────────────────────────────

async def run_schedule(agent: AgentMacSDK, interval: int, task: str) -> None:
    """Executa uma task em intervalos regulares."""
    console.print(f"[cyan]⏱ Schedule:[/cyan] every {interval}s")
    console.print(f"[cyan]📋 Task:[/cyan] {task}\n")

    run_count = 0
    while True:
        run_count += 1
        console.print(Rule(f"[dim]Run #{run_count} — {time.strftime('%H:%M:%S')}[/dim]"))

        dynamic_task = task.format(
            run_count=run_count,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        )

        try:
            result = await agent.query(dynamic_task)
            console.print(f"[green]✓[/green] {result[:400]}")
        except Exception as e:
            console.print(f"[red]✗ Error:[/red] {e}")

        console.print(f"[dim]Next run in {interval}s...[/dim]")
        await asyncio.sleep(interval)


# ─── Mode 3: HTTP API Server ─────────────────────────────────────────────────

def run_api(agent: AgentMacSDK, port: int = 8080) -> None:
    """
    Servidor HTTP minimalista.

    POST /query   body: {"prompt": "..."}   → {"result": "..."}
    GET  /health                             → {"status": "ok", "memory": {...}}
    GET  /skills                             → {"skills": [...]}
    """
    loop = asyncio.new_event_loop()

    auth_token = agent.config.server_auth_token
    cors_enabled = agent.config.cors_enabled

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            console.print(f"[dim]{self.address_string()} {fmt % args}[/dim]")

        def _check_auth(self) -> bool:
            """Validate auth token if configured."""
            if not auth_token:
                return True
            header = self.headers.get("Authorization", "")
            if header == f"Bearer {auth_token}":
                return True
            self._respond(401, b'{"error": "unauthorized"}')
            return False

        def _add_cors(self) -> None:
            """Add CORS headers for remote connections."""
            if cors_enabled:
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

        def do_OPTIONS(self):
            """Handle CORS preflight requests."""
            self.send_response(204)
            self._add_cors()
            self.end_headers()

        def do_GET(self):
            if not self._check_auth():
                return
            if self.path == "/health":
                body = json.dumps({
                    "status": "ok",
                    "memory": agent.episodic.summary(),
                }).encode()
                self._respond(200, body)

            elif self.path == "/skills":
                from pathlib import Path
                skills = [f.stem for f in Path(agent.config.skills_dir).glob("*.py")
                          if not f.name.startswith("_")]
                body = json.dumps({"skills": skills}).encode()
                self._respond(200, body)

            else:
                self._respond(404, b'{"error": "not found"}')

        def do_POST(self):
            if not self._check_auth():
                return
            if self.path != "/query":
                self._respond(404, b'{"error": "not found"}')
                return

            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            try:
                payload = json.loads(raw)
                prompt = payload.get("prompt", "")
                if not prompt:
                    self._respond(400, b'{"error": "missing prompt"}')
                    return

                future = asyncio.run_coroutine_threadsafe(agent.query(prompt), loop)
                result = future.result(timeout=300)
                body = json.dumps({"result": result}).encode()
                self._respond(200, body)

            except Exception as e:
                body = json.dumps({"error": str(e)}).encode()
                self._respond(500, body)

        def _respond(self, status: int, body: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(body))
            self._add_cors()
            self.end_headers()
            self.wfile.write(body)

    # Run asyncio loop in background thread
    def run_loop():
        loop.run_forever()

    t = Thread(target=run_loop, daemon=True)
    t.start()

    server = HTTPServer(("0.0.0.0", port), Handler)
    console.print(Rule("[bold cyan]Agent-MAC API Server[/bold cyan]"))
    console.print(f"[green]✓ Listening on http://0.0.0.0:{port}[/green]")
    console.print("[dim]POST /query  {\"prompt\": \"...\"}[/dim]")
    console.print("[dim]GET  /health[/dim]")
    console.print("[dim]GET  /skills[/dim]")
    if auth_token:
        console.print("[yellow]🔒 Auth token required (set via AGENT_MAC_AUTH_TOKEN)[/yellow]")
    else:
        console.print("[dim]⚠ No auth token — open access[/dim]")
    if cors_enabled:
        console.print("[dim]🌐 CORS enabled for remote connections[/dim]")
    console.print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down...[/yellow]")
        loop.call_soon_threadsafe(loop.stop)


# ─── CLI ──────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(description="Agent-MAC 24/7 Server")
    sub = parser.add_subparsers(dest="mode", required=True)

    # watch
    w = sub.add_parser("watch", help="Watch files and trigger agent on changes")
    w.add_argument("--path", default=".", help="Path to watch (file or directory)")
    w.add_argument("--task", required=True,
                   help="Task template. Use {files}, {file_count}, {timestamp}")
    w.add_argument("--cooldown", type=int, default=10, help="Seconds between triggers")

    # schedule
    s = sub.add_parser("schedule", help="Run agent on a fixed interval")
    s.add_argument("--interval", type=int, default=3600, help="Interval in seconds")
    s.add_argument("--task", required=True,
                   help="Task template. Use {run_count}, {timestamp}")

    # api
    a = sub.add_parser("api", help="Run as HTTP API server")
    a.add_argument("--port", type=int, default=8080, help="HTTP port")

    return parser.parse_args()


async def async_main():
    args = parse_args()
    config = AgentConfig()
    agent = AgentMacSDK(config)

    if args.mode == "watch":
        await run_watch(agent, args.path, args.task, args.cooldown)
    elif args.mode == "schedule":
        await run_schedule(agent, args.interval, args.task)
    elif args.mode == "api":
        run_api(agent, args.port)  # blocking


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
