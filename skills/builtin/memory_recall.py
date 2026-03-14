"""
Built-in skill: memory_recall
Retrieves stored facts from persistent memory.
"""
# SKILL_META
NAME = "memory_recall"
DESCRIPTION = "Recall stored facts or information from persistent memory"
PARAMETERS = {
    "type": "object",
    "properties": {
        "key": {
            "type": "string",
            "description": "Specific key to retrieve (leave empty to list all)"
        },
        "category": {
            "type": "string",
            "description": "Filter by category: 'fact', 'preference', 'solution', 'lesson'"
        }
    },
    "required": [],
}

import json
from pathlib import Path

MEMORY_FILE = Path(".memory/semantic.json")


async def run(params: dict) -> str:
    try:
        if not MEMORY_FILE.exists():
            return "Memory is empty."

        data = json.loads(MEMORY_FILE.read_text())

        key = params.get("key", "")
        category = params.get("category", "")

        if key:
            entry = data.get(key)
            return f"{key}: {entry['value']}" if entry else f"No memory for key '{key}'"

        if category:
            matches = {k: v for k, v in data.items() if v.get("category") == category}
            if not matches:
                return f"No memories in category '{category}'"
            return json.dumps(matches, indent=2)

        return json.dumps(data, indent=2)

    except Exception as e:
        return f"Memory recall error: {e}"
