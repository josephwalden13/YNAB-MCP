import json
from json import dumps
from typing import Any
from mcp.server.fastmcp import FastMCP
from tools.api_client import GetError, ynab_get


class Budget:
    id: str | None
    name: str | None
    first_month: str | None
    last_month: str | None

    def __init__(self, json: dict[str, Any]):
        self.id = json.get("id")
        self.name = json.get("name")
        self.first_month = json.get("first_month")
        self.last_month = json.get("last_month")

    def toJson(self) -> dict[str, Any]:
        json = {
            "id": self.id,
            "name": self.name,
            "first_month": self.first_month,
            "last_month": self.last_month,
        }
        return {x: json[x] for x in json if json[x] is not None}


async def _get_budgets() -> list[Budget]:
    response = await ynab_get("/budgets")
    if not response:
        raise GetError({"error": "Unable to fetch budgets.", "response": response})
    if not "budgets" in response:
        raise GetError(
            {"error": "No budgets found in response", "response": response}
        )
    budgets = [Budget(x) for x in response["budgets"]]
    return budgets


def register_budget_tools(mcp: FastMCP):
    """Register budget-related MCP tools."""

    @mcp.tool()
    async def get_budgets() -> str:
        """Fetch budgets from YNAB API."""
        budgets = await _get_budgets()
        return dumps([x.toJson() for x in budgets])
