import json
from mcp.server.fastmcp import FastMCP
from .api_client import ynab_get


def format_budgets(budgets):
    return json.dumps(
        [
            {
                "id": budget["id"],
                "name": budget["name"],
                "first_month": budget["first_month"],
                "last_month": budget["last_month"],
            }
            for budget in budgets
        ]
    )


def register_budget_tools(mcp: FastMCP):
    """Register budget-related MCP tools."""

    @mcp.tool()
    async def get_budgets() -> str:
        """Fetch budgets from YNAB API."""
        response = await ynab_get("budgets")
        if not response:
            return "Unable to fetch budgets."
        assert "budgets" in response, "No budgets found in response"
        budgets = response["budgets"]
        return format_budgets(budgets)
