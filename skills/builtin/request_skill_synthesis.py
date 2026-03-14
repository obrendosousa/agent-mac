"""
Built-in skill: request_skill_synthesis

This is the KEY self-programming skill.
When the agent needs a capability that doesn't exist, it calls this tool
to trigger the MetaProgrammer to synthesize a new Python tool at runtime.
"""
# SKILL_META
NAME = "request_skill_synthesis"
DESCRIPTION = (
    "Request the creation of a new tool/skill that doesn't currently exist. "
    "The system will synthesize Python code for the capability and register "
    "it immediately so you can use it in this session."
)
PARAMETERS = {
    "type": "object",
    "properties": {
        "capability": {
            "type": "string",
            "description": "Natural language description of the capability needed"
        },
        "examples": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Optional example use cases or inputs/outputs",
        }
    },
    "required": ["capability"],
}


# The actual handler is injected at agent startup time.
# This placeholder is replaced by the MetaProgrammer-aware version in agent.py.

async def run(params: dict) -> str:
    return (
        "Skill synthesis handler not yet initialized. "
        "This is replaced at agent startup by the MetaProgrammer."
    )
