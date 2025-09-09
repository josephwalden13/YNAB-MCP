import json
from json import dumps
from typing import Any
from mcp.server.fastmcp import FastMCP
from tools.api_client import GetError, ynab_get


class User:
    id: str | None

    def __init__(self, json: dict[str, Any]):
        self.id = json.get("id")

    def toJson(self) -> dict[str, Any]:
        json = {
            "id": self.id,
        }
        return {x: json[x] for x in json if json[x] is not None}


async def _get_user() -> User:
    response = await ynab_get("/user")
    if not response:
        raise GetError({"error": "Unable to fetch user information.", "response": response})
    if not "user" in response:
        raise GetError(
            {"error": "No user found in response", "response": response}
        )
    return User(response["user"])


def register_user_tools(mcp: FastMCP):
    """Register user-related MCP tools."""

    @mcp.tool()
    async def get_user() -> str:
        """Fetch user information from YNAB API."""
        user = await _get_user()
        return json.dumps(user.toJson())
