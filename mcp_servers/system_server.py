import json
from datetime import datetime
from zoneinfo import ZoneInfo

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("system-server")


def current_time_data(timezone: str = "UTC") -> dict[str, str]:
    """Return timestamp data for server tools that need it.

    This is ordinary Python, not an MCP tool. Other server code may import it
    when it needs the same timestamp behavior.
    """
    try:
        tz = ZoneInfo(timezone)
    except Exception:
        timezone = "UTC"
        tz = ZoneInfo(timezone)
    return {
        "timezone": timezone,
        "iso": datetime.now(tz).isoformat(timespec="seconds"),
    }


@mcp.tool()
def get_current_time(timezone: str = "UTC") -> str:
    """Return the current time as an ISO-8601 string."""
    return json.dumps(current_time_data(timezone))


if __name__ == "__main__":
    mcp.run()
