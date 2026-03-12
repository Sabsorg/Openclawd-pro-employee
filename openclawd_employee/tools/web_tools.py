"""HTTP request tool for web interactions."""

from __future__ import annotations

from typing import Any

from openclawd_employee.tools.base import Tool


class HttpRequestTool(Tool):
    """Perform an HTTP request and return the response body."""

    @property
    def name(self) -> str:
        return "http_request"

    @property
    def description(self) -> str:
        return "Make an HTTP request (GET, POST, etc.) and return the response."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The URL to request."},
                "method": {
                    "type": "string",
                    "description": "HTTP method (GET, POST, PUT, DELETE, PATCH).",
                    "default": "GET",
                },
                "body": {
                    "type": "string",
                    "description": "Optional request body (for POST/PUT/PATCH).",
                    "default": "",
                },
                "headers": {
                    "type": "object",
                    "description": "Optional HTTP headers as key-value pairs.",
                    "default": {},
                },
            },
            "required": ["url"],
        }

    async def run(self, **kwargs: Any) -> str:
        try:
            import httpx  # noqa: E402 – lazy import keeps the dep optional
        except ImportError:
            return "httpx is not installed. Run: pip install httpx"

        url: str = kwargs["url"]
        method: str = kwargs.get("method", "GET").upper()
        body: str = kwargs.get("body", "")
        headers: dict[str, str] = kwargs.get("headers", {})

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.request(
                    method,
                    url,
                    content=body if body else None,
                    headers=headers,
                )
                return (
                    f"HTTP {response.status_code}\n"
                    f"{response.text[:4000]}"
                )
        except httpx.HTTPError as exc:
            return f"HTTP error: {exc}"
