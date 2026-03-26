"""HTTP request tool for web interactions."""

from __future__ import annotations

import ipaddress
from typing import Any
from urllib.parse import urlparse

from openclawd_employee.tools.base import Tool

# IP ranges that are blocked by default to prevent SSRF.
_BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]


def _is_blocked_host(hostname: str) -> bool:
    """Return True if *hostname* resolves to a private/loopback address."""
    if not hostname or hostname.lower() == "localhost":
        return True
    try:
        addr = ipaddress.ip_address(hostname)
        return any(addr in net for net in _BLOCKED_NETWORKS)
    except ValueError:
        # Not a literal IP — allow DNS hostnames through.
        return False


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

        # SSRF guard: block requests to private/loopback addresses.
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname or ""
        if _is_blocked_host(hostname):
            return f"Blocked: requests to private/loopback addresses are not allowed ({hostname})"

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
