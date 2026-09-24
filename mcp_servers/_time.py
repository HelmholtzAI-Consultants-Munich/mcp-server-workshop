"""Shared time helpers for MCP servers.

This module holds ordinary Python logic. Server modules wrap it in their own
MCP tools rather than calling one another's decorated functions directly.
"""
from datetime import datetime
from zoneinfo import ZoneInfo


def current_time(timezone: str = "UTC") -> dict[str, str]:
    """Return the current ISO-8601 time, falling back to UTC when needed."""
    try:
        tz = ZoneInfo(timezone)
    except Exception:
        timezone = "UTC"
        tz = ZoneInfo(timezone)
    return {
        "timezone": timezone,
        "iso": datetime.now(tz).isoformat(timespec="seconds"),
    }
