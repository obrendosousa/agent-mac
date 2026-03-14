"""
Built-in skill: web_fetch
Fetches content from a URL and returns the text.
"""
# SKILL_META
NAME = "web_fetch"
DESCRIPTION = "Fetch the text content of a web page given its URL"
PARAMETERS = {
    "type": "object",
    "properties": {
        "url": {
            "type": "string",
            "description": "The URL to fetch"
        },
        "max_chars": {
            "type": "integer",
            "description": "Maximum characters to return (default: 4000)",
        }
    },
    "required": ["url"],
}


async def run(params: dict) -> str:
    try:
        import httpx
        url = params["url"]
        max_chars = params.get("max_chars", 4000)

        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
            response = await client.get(url, headers={"User-Agent": "agent-mac/0.1"})
            response.raise_for_status()
            text = response.text

        # Simple HTML tag stripping
        import re
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:max_chars]

    except Exception as e:
        return f"Error fetching {params.get('url')}: {e}"
