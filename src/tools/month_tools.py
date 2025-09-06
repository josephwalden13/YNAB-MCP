import json
from mcp.server.fastmcp import FastMCP
from .api_client import format_error, ynab_get, ynab_put


def format_months(months):
    return json.dumps(
        [
            {
                "month": month["month"],
                "note": month["note"],
                "income": (month["income"] or 0) / 1000,
                "budgeted": (month["budgeted"] or 0) / 1000,
                "activity": (month["activity"] or 0) / 1000,
                "to_be_budgeted": (month["to_be_budgeted"] or 0) / 1000,
                "age_of_money": month["age_of_money"],
                "deleted": month["deleted"],
            }
            for month in months
        ]
    )


def register_month_tools(mcp: FastMCP):
    """Register month-related MCP tools."""

    @mcp.tool()
    async def get_months(budget_id: str) -> str:
        """Fetch months from YNAB API."""
        response = await ynab_get(f"budgets/{budget_id}/months")
        if not response:
            return format_error("Unable to fetch months.")
        if not "months" in response:
            return format_error("No months found in response.", response=response)
        months = response["months"]
        return format_months(months)
