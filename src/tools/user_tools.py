import json
from mcp.server.fastmcp import FastMCP
from .api_client import format_error, ynab_get


def format_user(user):
    return json.dumps(
        {
            "id": user["id"],
        }
    )


def register_user_tools(mcp: FastMCP):
    """Register user-related MCP tools."""

    @mcp.tool()
    async def get_user() -> str:
        """Fetch user information from YNAB API."""
        response = await ynab_get("user")
        if not response:
            return format_error("Unable to fetch user information.")
        if not "user" in response:
            return format_error("No user found in response.", response=response)
        user = response["user"]
        return format_user(user)
