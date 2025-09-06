import json
from mcp.server.fastmcp import FastMCP
from .api_client import ynab_get


def register_payee_tools(mcp: FastMCP):
    """Register payee-related MCP tools."""

    @mcp.tool()
    async def get_payees(budget_id: str) -> str:
        """Fetch payees from YNAB API."""
        response = await ynab_get(f"budgets/{budget_id}/payees")
        if not response:
            return "Unable to fetch payees."
        assert "payees" in response, "No payees found in response"
        payees = response["payees"]
        return json.dumps(payees)
