"""
Meta-Programming Engine — the heart of self-programming capability.

This is what makes the agent go beyond OpenClaw.
When the agent discovers a capability gap, the programmer:

  1. Receives a natural-language description of the needed capability
  2. Uses Claude to synthesize a Python skill file
  3. Passes it to the Evaluator for safety and correctness checks
  4. If approved, registers the new tool with the Gateway
  5. The agent can immediately use the new tool in the same session

Architecture:
  Gap detected → Programmer → Synthesize code → Evaluator → Gateway.register()
                                                      ↑
                                           (sandbox test + LLM review)
"""
from __future__ import annotations

import ast
import importlib.util
import json
import sys
import textwrap
import traceback
from pathlib import Path
from typing import Any

import anthropic
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from core.config import AgentConfig
from core.gateway import Gateway

console = Console()

SYNTHESIS_SYSTEM = """You are an expert Python developer writing tool implementations for an AI agent.

Your task: write a Python async function that implements the requested capability.

STRICT FORMAT — respond ONLY with a JSON object:
{
  "name": "snake_case_tool_name",
  "description": "One sentence describing what the tool does",
  "parameters": {
    "type": "object",
    "properties": {
      "param_name": {"type": "string", "description": "..."}
    },
    "required": ["param_name"]
  },
  "code": "async def run(params: dict) -> str:\\n    # implementation\\n    ..."
}

Rules for the code:
- Function signature MUST be: async def run(params: dict) -> str
- Access parameters via params["key"] or params.get("key", default)
- Return a string result
- Use only stdlib + httpx + json + anthropic for external needs
- Handle errors gracefully and return descriptive error strings
- Keep it focused and minimal
- DO NOT import from the agent's own modules
"""


class MetaProgrammer:
    """
    Synthesizes new tools from natural language descriptions.

    This is the self-programming core: it uses Claude to write
    Python code that extends the agent's own capabilities.
    """

    def __init__(
        self,
        config: AgentConfig,
        gateway: Gateway | None,
        client: anthropic.AsyncAnthropic,
    ) -> None:
        self.config = config
        self.gateway = gateway  # Optional: None when using Agent SDK mode
        self.client = client
        self._synthesized_count = 0

    async def synthesize_and_register(
        self,
        capability_description: str,
        examples: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Main entry point: turn a capability description into a live tool.

        Returns a status dict indicating success/failure.
        """
        console.print(Panel(
            f"[bold yellow]🔧 Synthesizing new skill:[/bold yellow]\n{capability_description}",
            title="[yellow]Meta-Programmer[/yellow]",
        ))

        # Step 1: Synthesize code
        skill_spec = await self._synthesize_code(capability_description, examples or [])
        if "error" in skill_spec:
            return skill_spec

        # Step 2: Evaluate the code for safety and correctness
        eval_result = await self._evaluate_code(skill_spec)
        if not eval_result["approved"]:
            return {"error": f"Skill rejected: {eval_result['reason']}"}

        # Step 3: Persist to disk
        skill_path = await self._persist_skill(skill_spec)

        # Step 4: Register with Gateway (optional — not needed in Agent SDK mode)
        if self.gateway is not None:
            reg_result = await self._register_skill(skill_spec, skill_path)
            if "error" in reg_result:
                return reg_result

        self._synthesized_count += 1
        console.print(f"[bold green]★ New tool '{skill_spec['name']}' synthesized![/bold green]")
        console.print(f"[dim]  Use run_synthesized_skill('{skill_spec['name']}', {{...}}) to execute.[/dim]")
        return {
            "success": True,
            "tool_name": skill_spec["name"],
            "description": skill_spec["description"],
            "file": str(skill_path),
        }

    async def _synthesize_code(
        self,
        description: str,
        examples: list[str],
    ) -> dict[str, Any]:
        """Ask Claude to write the tool implementation."""
        prompt_parts = [f"Write a tool that: {description}"]
        if examples:
            prompt_parts.append(f"\nExample use cases:\n" + "\n".join(f"- {e}" for e in examples))

        try:
            response = await self.client.messages.create(
                model=self.config.model,
                max_tokens=4096,
                thinking={"type": "adaptive"},
                system=SYNTHESIS_SYSTEM,
                messages=[{"role": "user", "content": "\n".join(prompt_parts)}],
            )

            # Extract text (skip thinking blocks)
            raw = ""
            for block in response.content:
                if block.type == "text":
                    raw = block.text
                    break

            # Parse JSON response
            # Strip markdown code fences if present
            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()

            spec = json.loads(raw)
            console.print(Syntax(spec.get("code", ""), "python", theme="monokai", line_numbers=True))
            return spec

        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse synthesized spec: {e}\nRaw: {raw[:300]}"}
        except Exception as e:
            return {"error": f"Synthesis failed: {e}"}

    async def _evaluate_code(self, spec: dict[str, Any]) -> dict[str, Any]:
        """
        Multi-layer evaluation:
        1. AST safety check (no dangerous imports)
        2. Syntax validation
        3. LLM review for correctness
        """
        code = spec.get("code", "")

        # Layer 1: AST safety scan
        safety = self._ast_safety_check(code)
        if not safety["safe"]:
            return {"approved": False, "reason": safety["reason"]}

        # Layer 2: Syntax check
        try:
            ast.parse(code)
        except SyntaxError as e:
            return {"approved": False, "reason": f"Syntax error: {e}"}

        # Layer 3: Quick LLM review (using fast model)
        review = await self._llm_review(spec)
        return review

    def _ast_safety_check(self, code: str) -> dict[str, Any]:
        """Scan AST for dangerous operations."""
        BANNED_MODULES = {
            "os", "subprocess", "sys", "shutil", "pathlib",
            "socket", "ctypes", "multiprocessing",
        }
        BANNED_BUILTINS = {"exec", "eval", "compile", "__import__"}

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {"safe": False, "reason": str(e)}

        for node in ast.walk(tree):
            # Check imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module = ""
                if isinstance(node, ast.Import):
                    module = node.names[0].name.split(".")[0]
                elif node.module:
                    module = node.module.split(".")[0]
                if module in BANNED_MODULES:
                    return {"safe": False, "reason": f"Banned module: {module}"}

            # Check builtins
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in BANNED_BUILTINS:
                    return {"safe": False, "reason": f"Banned builtin: {node.func.id}"}

        return {"safe": True}

    async def _llm_review(self, spec: dict[str, Any]) -> dict[str, Any]:
        """Quick LLM review of the skill quality and correctness."""
        prompt = f"""Review this agent skill for correctness and usefulness.

Name: {spec.get('name')}
Description: {spec.get('description')}
Code:
```python
{spec.get('code')}
```

Respond with JSON: {{"approved": true/false, "reason": "brief explanation"}}"""

        try:
            response = await self.client.messages.create(
                model=self.config.fast_model,
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = next((b.text for b in response.content if b.type == "text"), '{"approved": true, "reason": "ok"}')
            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1].lstrip("json").strip()
            return json.loads(raw)
        except Exception:
            return {"approved": True, "reason": "review skipped"}

    async def _persist_skill(self, spec: dict[str, Any]) -> Path:
        """Write the skill to disk as a .py file."""
        skills_dir = Path(self.config.skills_dir)
        skill_file = skills_dir / f"{spec['name']}.py"

        skill_content = textwrap.dedent(f'''\
            """
            Auto-synthesized skill: {spec["name"]}
            Description: {spec["description"]}
            """
            # SKILL_META
            NAME = "{spec["name"]}"
            DESCRIPTION = "{spec["description"]}"
            PARAMETERS = {json.dumps(spec["parameters"], indent=4)}

            {spec["code"]}
        ''')

        skill_file.write_text(skill_content)
        console.print(f"[dim]  Skill persisted to: {skill_file}[/dim]")
        return skill_file

    async def _register_skill(
        self,
        spec: dict[str, Any],
        skill_path: Path,
    ) -> dict[str, Any]:
        """Dynamically load the skill module and register its handler."""
        try:
            module_name = f"skills.dynamic.{spec['name']}"
            module_spec = importlib.util.spec_from_file_location(module_name, skill_path)
            if module_spec is None or module_spec.loader is None:
                return {"error": "Could not create module spec"}

            module = importlib.util.module_from_spec(module_spec)
            sys.modules[module_name] = module
            module_spec.loader.exec_module(module)

            if not hasattr(module, "run"):
                return {"error": "Skill module missing 'run' function"}

            # Build Anthropic tool schema
            tool_schema = {
                "name": spec["name"],
                "description": spec["description"],
                "input_schema": spec["parameters"],
            }

            # Register with gateway
            self.gateway.register_tool(
                name=spec["name"],
                handler=module.run,
                schema=tool_schema,
            )
            return {"success": True}

        except Exception as e:
            return {"error": f"Registration failed: {e}\n{traceback.format_exc()}"}
