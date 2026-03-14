"""
Built-in skill: memory_store
Saves a key-value fact to persistent memory.
"""
# SKILL_META
NAME = "memory_store"
DESCRIPTION = "Store a fact or piece of information in persistent memory for future sessions"
PARAMETERS = {
    "type": "object",
    "properties": {
        "key": {
            "type": "string",
            "description": "Unique key to identify this memory (e.g. 'user_preference_language')"
        },
        "value": {
            "type": "string",
            "description": "The information to store"
        },
        "category": {
            "type": "string",
            "description": "Category: 'fact', 'preference', 'solution', 'lesson'",
        }
    },
    "required": ["key", "value"],
}

import json
from pathlib import Path

MEMORY_FILE = Path(".memory/semantic.json")


async def run(params: dict) -> str:
    try:
        MEMORY_FILE.parent.mkdir(exist_ok=True)
        data = {}
        if MEMORY_FILE.exists():
            data = json.loads(MEMORY_FILE.read_text())

        key = params["key"]
        data[key] = {
            "value": params["value"],
            "category": params.get("category", "fact"),
        }
        MEMORY_FILE.write_text(json.dumps(data, indent=2))
        return f"Stored: '{key}'"
    except Exception as e:
        return f"Memory store error: {e}"
