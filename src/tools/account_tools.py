import json
from json import dumps
from typing import Any
from mcp.server.fastmcp import FastMCP
from tools.api_client import (
    GetError,
    ynab_get,
)


class Account:
    id: str | None
    name: str | None
    type: str | None
    on_budget: bool | None
    closed: bool | None
    note: str | None
    balance: float | None
    cleared_balance: float | None
    uncleared_balance: float | None
    transfer_payee_id: str | None
    last_reconciled_at: str | None
    debt_original_balance: float | None
    debt_interest_rates: dict[str, float] | None
    debt_minimum_payments: dict[str, float] | None
    debt_escrow_amounts: dict[str, float] | None
    deleted: bool | None

    def __init__(self, json: dict[str, Any]):
        self.id = json.get("id")
        self.name = json.get("name")
        self.type = json.get("type")
        self.on_budget = json.get("on_budget")
        self.closed = json.get("closed")
        self.note = json.get("note")
        self.balance = (json["balance"] or 0) / 1000 if json.get("balance") is not None else None
        self.cleared_balance = (json["cleared_balance"] or 0) / 1000 if json.get("cleared_balance") is not None else None
        self.uncleared_balance = (json["uncleared_balance"] or 0) / 1000 if json.get("uncleared_balance") is not None else None
        self.transfer_payee_id = json.get("transfer_payee_id")
        self.last_reconciled_at = json.get("last_reconciled_at")
        self.debt_original_balance = (json["debt_original_balance"] or 0) / 1000 if json.get("debt_original_balance") is not None else None
        self.debt_interest_rates = self._format_monthly_balances(json, "debt_interest_rates") if json.get("debt_interest_rates") else None
        self.debt_minimum_payments = self._format_monthly_balances(json, "debt_minimum_payments") if json.get("debt_minimum_payments") else None
        self.debt_escrow_amounts = self._format_monthly_balances(json, "debt_escrow_amounts") if json.get("debt_escrow_amounts") else None
        self.deleted = json.get("deleted")

    def _format_monthly_balances(self, json: dict[str, Any], key: str) -> dict[str, float]:
        monthly_balances = json.get(key, {})
        return {x: (monthly_balances[x] or 0) / 1000 for x in monthly_balances}

    def toJson(self) -> dict[str, Any]:
        json = {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "on_budget": self.on_budget,
            "closed": self.closed,
            "note": self.note,
            "balance": self.balance,
            "cleared_balance": self.cleared_balance,
            "uncleared_balance": self.uncleared_balance,
            "transfer_payee_id": self.transfer_payee_id,
            "last_reconciled_at": self.last_reconciled_at,
            "debt_original_balance": self.debt_original_balance,
            "debt_interest_rates": self.debt_interest_rates,
            "debt_minimum_payments": self.debt_minimum_payments,
            "debt_escrow_amounts": self.debt_escrow_amounts,
            "deleted": self.deleted,
        }
        return {x: json[x] for x in json if json[x] is not None}


async def _get_accounts(budget_id: str = "last-used") -> list[Account]:
    response = await ynab_get(f"/budgets/{budget_id}/accounts")
    if not response:
        raise GetError({"error": "Unable to fetch accounts.", "response": response})
    if not "accounts" in response:
        raise GetError(
            {"error": "No accounts found in response", "response": response}
        )
    accounts = [Account(x) for x in response["accounts"]]
    return accounts


def register_account_tools(mcp: FastMCP):
    """Register account-related MCP tools."""

    @mcp.tool()
    async def get_accounts(budget_id: str = "last-used") -> str:
        """Fetch accounts from YNAB API.
        Args:
            budget_id (str, optional): The ID of the budget. If not provided the last used budget will be used.
        """
        accounts = await _get_accounts(budget_id)
        return dumps([x.toJson() for x in accounts])
