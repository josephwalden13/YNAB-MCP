import json
from mcp.server.fastmcp import FastMCP
from .api_client import format_error, ynab_get


def register_payee_tools(mcp: FastMCP):
    """Register payee-related MCP tools."""

    @mcp.tool()
    async def get_payees(budget_id: str) -> str:
        """Fetch payees from YNAB API."""
        response = await ynab_get(f"budgets/{budget_id}/payees")
        if not response:
            return format_error("Unable to fetch payees.")
        if not "payees" in response:
            return format_error("No payees found in response.", response=response)
        payees = response["payees"]
        return json.dumps(payees)
