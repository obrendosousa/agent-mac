"""
Built-in skill: connect_to_pc
Connects to a remote Agent-MAC API server running on a PC.
Allows sending queries, checking health, and listing skills remotely.
"""
# SKILL_META
NAME = "connect_to_pc"
DESCRIPTION = (
    "Connect to a remote Agent-MAC server running on your PC. "
    "Supports sending queries, checking health, and listing remote skills."
)
PARAMETERS = {
    "type": "object",
    "properties": {
        "action": {
            "type": "string",
            "enum": ["connect", "query", "health", "skills", "disconnect", "status"],
            "description": (
                "Action to perform: "
                "'connect' to establish connection, "
                "'query' to send a prompt, "
                "'health' to check server health, "
                "'skills' to list remote skills, "
                "'disconnect' to close connection, "
                "'status' to check connection status"
            ),
        },
        "host": {
            "type": "string",
            "description": "PC hostname or IP address (e.g., '192.168.1.100' or 'my-pc.local')",
        },
        "port": {
            "type": "integer",
            "description": "Port where Agent-MAC API is running (default: 8080)",
        },
        "prompt": {
            "type": "string",
            "description": "Prompt to send when action is 'query'",
        },
        "auth_token": {
            "type": "string",
            "description": "Optional authentication token for secured connections",
        },
        "timeout": {
            "type": "integer",
            "description": "Request timeout in seconds (default: 30, max: 300 for queries)",
        },
    },
    "required": ["action"],
}

# In-memory connection state
_connection = {
    "connected": False,
    "host": None,
    "port": None,
    "auth_token": None,
    "base_url": None,
}


async def run(params: dict) -> str:
    import httpx
    import json

    action = params.get("action", "status")
    timeout = min(params.get("timeout", 30), 300)

    if action == "connect":
        host = params.get("host")
        port = params.get("port", 8080)
        auth_token = params.get("auth_token")

        if not host:
            return "Error: 'host' is required for connect. Provide your PC's IP or hostname."

        base_url = f"http://{host}:{port}"
        _connection["host"] = host
        _connection["port"] = port
        _connection["auth_token"] = auth_token
        _connection["base_url"] = base_url

        # Test connection with health check
        try:
            headers = {}
            if auth_token:
                headers["Authorization"] = f"Bearer {auth_token}"

            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.get(f"{base_url}/health", headers=headers)
                resp.raise_for_status()
                data = resp.json()

            _connection["connected"] = True
            memory_info = data.get("memory", {})
            return (
                f"Connected to Agent-MAC on {host}:{port}\n"
                f"Status: {data.get('status', 'unknown')}\n"
                f"Sessions: {memory_info.get('total_episodes', 0)}\n"
                f"Avg effectiveness: {memory_info.get('avg_effectiveness', 'N/A')}"
            )
        except httpx.ConnectError:
            _connection["connected"] = False
            return (
                f"Could not connect to {base_url}\n"
                f"Make sure Agent-MAC server is running on your PC:\n"
                f"  python server.py api --port {port}"
            )
        except Exception as e:
            _connection["connected"] = False
            return f"Connection failed: {e}"

    elif action == "status":
        if _connection["connected"]:
            return (
                f"Connected to {_connection['host']}:{_connection['port']}\n"
                f"URL: {_connection['base_url']}"
            )
        return "Not connected. Use action 'connect' with your PC's host/IP."

    elif action == "disconnect":
        was_connected = _connection["connected"]
        _connection.update({"connected": False, "host": None, "port": None, "auth_token": None, "base_url": None})
        return "Disconnected." if was_connected else "Was not connected."

    # Actions below require active connection
    if not _connection["connected"]:
        return "Not connected to any PC. Use action 'connect' first."

    base_url = _connection["base_url"]
    headers = {}
    if _connection["auth_token"]:
        headers["Authorization"] = f"Bearer {_connection['auth_token']}"

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:

            if action == "health":
                resp = await client.get(f"{base_url}/health", headers=headers)
                resp.raise_for_status()
                data = resp.json()
                memory = data.get("memory", {})
                return (
                    f"Server: {data.get('status', 'unknown')}\n"
                    f"Episodes: {memory.get('total_episodes', 0)}\n"
                    f"Skills synthesized: {memory.get('synthesized_skill_count', 0)}\n"
                    f"Avg effectiveness: {memory.get('avg_effectiveness', 'N/A')}"
                )

            elif action == "skills":
                resp = await client.get(f"{base_url}/skills", headers=headers)
                resp.raise_for_status()
                data = resp.json()
                skills = data.get("skills", [])
                if not skills:
                    return "No synthesized skills on remote server."
                return f"{len(skills)} remote skills:\n" + "\n".join(f"  - {s}" for s in skills)

            elif action == "query":
                prompt = params.get("prompt")
                if not prompt:
                    return "Error: 'prompt' is required for query action."
                resp = await client.post(
                    f"{base_url}/query",
                    json={"prompt": prompt},
                    headers=headers,
                    timeout=min(timeout, 300),
                )
                resp.raise_for_status()
                data = resp.json()
                if "error" in data:
                    return f"Remote error: {data['error']}"
                return f"Remote response:\n{data.get('result', '(empty)')}"

            else:
                return f"Unknown action: {action}. Use: connect, query, health, skills, disconnect, status."

    except httpx.ConnectError:
        _connection["connected"] = False
        return f"Connection lost to {_connection['host']}. Server may be offline."
    except httpx.TimeoutException:
        return f"Request timed out after {timeout}s. Try increasing timeout or check server load."
    except Exception as e:
        return f"Error: {e}"
