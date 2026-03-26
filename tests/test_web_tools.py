"""Tests for the HTTP request tool's SSRF protection."""

from __future__ import annotations

import pytest

from openclawd_employee.tools.web_tools import HttpRequestTool, _is_blocked_host


class TestSSRFProtection:
    def test_localhost_blocked(self) -> None:
        assert _is_blocked_host("localhost") is True

    def test_loopback_ip_blocked(self) -> None:
        assert _is_blocked_host("127.0.0.1") is True

    def test_private_10_blocked(self) -> None:
        assert _is_blocked_host("10.0.0.1") is True

    def test_private_172_blocked(self) -> None:
        assert _is_blocked_host("172.16.0.1") is True

    def test_private_192_blocked(self) -> None:
        assert _is_blocked_host("192.168.1.1") is True

    def test_link_local_blocked(self) -> None:
        assert _is_blocked_host("169.254.169.254") is True

    def test_public_ip_allowed(self) -> None:
        assert _is_blocked_host("8.8.8.8") is False

    def test_hostname_allowed(self) -> None:
        assert _is_blocked_host("example.com") is False


@pytest.mark.asyncio
async def test_http_request_blocks_localhost() -> None:
    tool = HttpRequestTool()
    result = await tool.run(url="http://localhost/secret")
    assert "Blocked" in result


@pytest.mark.asyncio
async def test_http_request_blocks_private_ip() -> None:
    tool = HttpRequestTool()
    result = await tool.run(url="http://169.254.169.254/metadata")
    assert "Blocked" in result
