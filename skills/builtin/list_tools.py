"""
Built-in skill: list_tools
Shows all currently available tools, including dynamically synthesized ones.
"""
# SKILL_META
NAME = "list_tools"
DESCRIPTION = "List all currently available tools/skills, including dynamically synthesized ones"
PARAMETERS = {
    "type": "object",
    "properties": {
        "filter": {
            "type": "string",
            "description": "Optional substring filter for tool names"
        }
    },
    "required": [],
}

# Handler is replaced at startup with a gateway-aware version
async def run(params: dict) -> str:
    return "Tool listing not yet initialized."
