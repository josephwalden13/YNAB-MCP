import json
from mcp.server.fastmcp import FastMCP
from .api_client import ynab_get


def format_monthly_balances(monthly_balances):
    return [{x: (monthly_balances[x] or 0) / 1000} for x in monthly_balances]


def format_accounts(accounts):
    return json.dumps(
        [
            {
                "id": account["id"],
                "name": account["name"],
                "type": account["type"],
                "on_budget": account["on_budget"],
                "closed": account["closed"],
                "note": account["note"],
                "balance": (account["balance"] or 0) / 1000,
                "cleared_balance": (account["cleared_balance"] or 0) / 1000,
                "uncleared_balance": (account["uncleared_balance"] or 0) / 1000,
                "transfer_payee_id": account["transfer_payee_id"],
                "last_reconciled_at": account["last_reconciled_at"],
                "debt_original_balance": (account["debt_original_balance"] or 0) / 1000,
                "debt_interest_rates": format_monthly_balances(
                    account["debt_interest_rates"]
                ),
                "debt_minimum_payments": format_monthly_balances(
                    account["debt_minimum_payments"]
                ),
                "debt_escrow_amounts": format_monthly_balances(
                    account["debt_escrow_amounts"]
                ),
                "deleted": account["deleted"],
            }
            for account in accounts
        ]
    )


def register_account_tools(mcp: FastMCP):
    """Register account-related MCP tools."""

    @mcp.tool()
    async def get_accounts(budget_id: str) -> str:
        """Fetch accounts from YNAB API."""
        response = await ynab_get(f"budgets/{budget_id}/accounts")
        if not response:
            return "Unable to fetch accounts."
        assert "accounts" in response, "No accounts found in response"
        accounts = response["accounts"]
        return format_accounts(accounts)
