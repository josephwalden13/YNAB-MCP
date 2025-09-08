import datetime
import json
from json import loads, dumps
from typing import Any
from mcp.server.fastmcp import FastMCP
from tools.api_client import (
    GetError,
    PostError,
    PutError,
    ynab_get,
    ynab_post,
    ynab_put,
    ynab_delete,
    format_error,
)


class Transaction:
    id: str | None
    date: datetime.date | None
    amount: float | None
    approved: bool | None
    account_id: str | None
    cleared: str | None
    category_id: str | None
    payee_name: str | None

    def __init__(self, json: dict[str, Any]):
        self.id = json.get("id")
        self.date = datetime.date.fromisoformat(json["date"]) if json.get("date") else None
        self.amount = json["amount"] / 1000 if json.get("amount") else None  # convert from milliunits to units
        self.cleared = json.get("cleared")
        self.approved = json.get("approved")
        self.account_id = json.get("account_id")
        self.category_id = json.get("category_id")
        self.payee_name = json.get("payee_name")
        # TODO: subtransactions

    def toJson(self) -> dict[str, Any]:
        json = {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "amount": int(self.amount * 1000) if self.amount else None,
            "cleared": self.cleared,
            "approved": self.approved,
            "account_id": self.account_id,
            "payee_name": self.payee_name,
            "category_id": self.category_id,
        }
        return {x: json[x] for x in json if json[x] is not None}


async def _get_transactions(
    budget_id: str = "last-used",
    category_id: str | None = None,
    account_id: str | None = None,
    month: str | None = None,
    payee_id: str | None = None,
    since: str | None = None,
) -> list[Transaction]:
    url: str = str()
    if category_id:
        url = f"/budgets/{budget_id}/categories/{category_id}/transactions"
    elif account_id:
        url = f"/budgets/{budget_id}/accounts/{account_id}/transactions"
    elif month:
        url = f"/budgets/{budget_id}/months/{month}/transactions"
    elif payee_id:
        url = f"/budgets/{budget_id}/payees/{payee_id}/transactions"
    else:
        url = f"/budgets/{budget_id}/transactions"

    if since:
        url += f"?since={since}"

    response = await ynab_get(url)
    if not response:
        raise GetError({"error": "Unable to fetch transactions.", "response": response})
    if not "transactions" in response:
        raise GetError(
            {"error": "No transactions found in response", "response": response}
        )
    transactions = [Transaction(x) for x in response["transactions"]]
    return transactions


async def _new_transaction(
    transaction: Transaction, budget_id: str = "last-used"
) -> Transaction:
    response = await ynab_post(
        f"/budgets/{budget_id}/transactions", {"transaction": transaction.toJson()}
    )
    if not response:
        raise PostError("Unable to create transaction.")
    if not "transaction" in response:
        raise PostError("No transaction found in response data.")
    return Transaction(response["transaction"])


async def _update_transaction(
    transaction: Transaction, budget_id: str = "last-used"
) -> Transaction:
    if not transaction.id:
        raise PutError("Transaction ID is required to update a transaction.")
    response = await ynab_put(
        f"/budgets/{budget_id}/transactions/{transaction.id}",
        {"transaction": transaction.toJson()},
    )
    if not response:
        raise PutError("Unable to update transaction.")
    if not "transaction" in response:
        raise PutError("No transaction found in response data.")
    return Transaction(response["transaction"])


def register_transaction_tools(mcp: FastMCP):
    """Register transaction-related MCP tools."""

    @mcp.tool()
    async def new_transaction(
        budget_id: str,
        date: str,
        amount: int,
        account_id: str,
        payee_name: str,
        category_id: str | None = None,
        memo: str | None = None,
    ) -> str:
        """Create a new transaction in YNAB API.
        Args:
            budget_id (str): The ID of the budget. If not provided the last used budget will be used.
            date (str): The date of the transaction in YYYY-MM-DD format.
            amount (int): The amount of the transaction in milliunits (e.g., $1.00 = 1000).
            account_id (str): The ID of the account.
            payee_name (str): The name of the payee.
            category_id (str, optional): The ID of the category.
            memo (str, optional): A memo for the transaction.
        """
        transaction = Transaction(
            {
                "account_id": account_id,
                "date": date,
                "amount": amount,
                "payee_name": payee_name,
                "category_id": category_id,
                "memo": memo,
                "approved": True,
            }
        )

        new_transaction = await _new_transaction(transaction, budget_id=budget_id)

        return json.dumps(new_transaction.toJson())

    # TODO: refactor
    @mcp.tool()
    async def update_transaction(
        budget_id: str,
        transaction_id: str,
        date: str | None = None,
        amount: int | None = None,
        account_id: str | None = None,
        payee_name: str | None = None,
        category_id: str | None = None,
        memo: str | None = None,
    ) -> str:
        """Update a transaction in YNAB API."""
        transaction = {}
        if date is not None:
            transaction["date"] = date
        if amount is not None:
            transaction["amount"] = amount
        if account_id is not None:
            transaction["account_id"] = account_id
        if payee_name is not None:
            transaction["payee_name"] = payee_name
        if category_id is not None:
            transaction["category_id"] = category_id
        if memo is not None:
            transaction["memo"] = memo

        transaction = Transaction(
            {
                "id": transaction_id,
                "account_id": account_id,
                "date": date,
                "amount": amount,
                "payee_name": payee_name,
                "category_id": category_id,
                "memo": memo,
                "approved": True,
            }
        )

        updated_transaction = await _update_transaction(
            transaction, budget_id=budget_id
        )

        return json.dumps(updated_transaction.toJson())

    # TODO: refactor
    @mcp.tool()
    async def delete_transaction(budget_id: str, transaction_id: str) -> str:
        """Delete a transaction in YNAB API."""
        response = await ynab_delete(
            f"budgets/{budget_id}/transactions/{transaction_id}"
        )
        if not response:
            return format_error("Unable to delete transaction.")
        return json.dumps(response)

    @mcp.tool()
    async def get_transactions_for_category(
        category_id: str, budget_id: str = "last-used", since: str | None = None
    ) -> str:
        """Fetch transactions from YNAB API for a specific category.
        Args:
            category_id (str): The ID of the category.
            budget_id (str, optional): The ID of the budget. If not provided the last used budget will be used.
            since (str, optional): Search for transactions after a specific date in YYYY-MM-DD format.
        """
        transactions = await _get_transactions(
            budget_id, category_id=category_id, since=since
        )
        return dumps([x.toJson() for x in transactions])

    @mcp.tool()
    async def get_transactions_for_account(
        account_id: str, budget_id: str = "last-used", since: str | None = None
    ) -> str:
        """Fetch transactions for a specific account from YNAB API.
        Args:
            account_id (str): The ID of the account.
            budget_id (str, optional): The ID of the budget. If not provided the last used budget will be used.
            since (str, optional): Search for transactions after a specific date in YYYY-MM-DD format.
        """
        transactions = await _get_transactions(
            budget_id, account_id=account_id, since=since
        )
        return dumps([x.toJson() for x in transactions])

    @mcp.tool()
    async def get_transactions_for_month(
        month: str = "current", budget_id: str = "last-used"
    ) -> str:
        """Fetch transactions for a specific month from YNAB API.
        Args:
            month (str, optional): The month to fetch transactions for in YYYY-MM-DD format. Defaults to the current month.
            budget_id (str, optional): The ID of the budget. If not provided the last used budget will be used.
        """
        transactions = await _get_transactions(budget_id, month=month)
        return dumps([x.toJson() for x in transactions])

    @mcp.tool()
    async def get_transactions_for_payee(
        payee_id: str, budget_id: str = "last-used", since: str | None = None
    ) -> str:
        """Fetch transactions for a specific payee from YNAB API.
        Args:
            payee_id (str): The ID of the payee.
            budget_id (str, optional): The ID of the budget. If not provided the last used budget will be used.
            since (str, optional): Search for transactions after a specific date in YYYY-MM-DD format.
        """
        transactions = await _get_transactions(
            budget_id, payee_id=payee_id, since=since
        )
        return dumps([x.toJson() for x in transactions])

    @mcp.tool()
    async def get_all_transactions(
        budget_id: str = "last-used", since: str | None = None
    ) -> str:
        """Fetch all transactions from YNAB API.
        Args:
            budget_id (str, optional): The ID of the budget. If not provided the last used budget will be used.
            since (str, optional): Search for transactions after a specific date in YYYY-MM-DD format.
        """
        transactions = await _get_transactions(budget_id, since=since)
        return dumps([x.toJson() for x in transactions])
