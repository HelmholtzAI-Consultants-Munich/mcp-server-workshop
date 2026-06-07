import json
from datetime import datetime
from zoneinfo import ZoneInfo

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("system-server")


@mcp.tool()
def get_current_time(timezone: str = "UTC") -> str:
    """Return the current time as an ISO-8601 string."""
    try:
        tz = ZoneInfo(timezone)
    except Exception:
        tz = ZoneInfo("UTC")
        timezone = "UTC"
    now = datetime.now(tz).isoformat(timespec="seconds")
    return json.dumps({"timezone": timezone, "iso": now})


if __name__ == "__main__":
    mcp.run()
