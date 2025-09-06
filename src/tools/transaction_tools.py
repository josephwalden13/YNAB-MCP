import json
from mcp.server.fastmcp import FastMCP
from tools.api_client import ynab_get, ynab_post, ynab_put, ynab_delete, format_error


def format_subtransactions(subtransactions):
    return [
        {
            "id": subtransaction["id"],
            "transaction_id": subtransaction["transaction_id"],
            "amount": (subtransaction["amount"] or 0) / 1000,
            "memo": subtransaction["memo"],
            "payee_id": subtransaction["payee_id"],
            "payee_name": subtransaction["payee_name"],
            "category_id": subtransaction["category_id"],
            "category_name": subtransaction["category_name"],
            "transfer_account_id": subtransaction["transfer_account_id"],
            "transfer_transaction_id": subtransaction["transfer_transaction_id"],
            "deleted": subtransaction["deleted"],
        }
        for subtransaction in subtransactions
    ]


def format_transactions(transactions):
    return json.dumps(
        [
            {
                "id": transaction["id"],
                "date": transaction["date"],
                "amount": (transaction["amount"] or 0) / 1000,
                "memo": transaction["memo"],
                "cleared": transaction["cleared"],
                "approved": transaction["approved"],
                "flag_color": transaction["flag_color"],
                "flag_name": transaction["flag_name"],
                "account_id": transaction["account_id"],
                "account_name": transaction["account_name"],
                "payee_id": transaction["payee_id"],
                "payee_name": transaction["payee_name"],
                "category_id": transaction["category_id"],
                "category_name": transaction["category_name"],
                "transfer_account_id": transaction["transfer_account_id"],
                "transfer_transaction_id": transaction["transfer_transaction_id"],
                "matched_transaction_id": transaction["matched_transaction_id"],
                "import_id": transaction["import_id"],
                "import_payee_name": transaction["import_payee_name"],
                "import_payee_name_original": transaction["import_payee_name_original"],
                "debt_transaction_type": transaction["debt_transaction_type"],
                "deleted": transaction["deleted"],
                "subtransactions": format_subtransactions(
                    transaction["subtransactions"]
                ),
            }
            for transaction in transactions
        ]
    )


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
        """Create a new transaction in YNAB API."""
        transaction_data = {
            "transaction": {
                "account_id": account_id,
                "date": date,
                "amount": amount,
                "payee_name": payee_name,
                "category_id": category_id,
                "memo": memo,
                "approved": True,
            }
        }

        response = await ynab_post(
            f"budgets/{budget_id}/transactions", transaction_data
        )
        if not response:
            return format_error("Unable to create transaction.")
        return json.dumps(response)

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
        transaction_data = {"transaction": transaction}

        response = await ynab_put(
            f"budgets/{budget_id}/transactions/{transaction_id}", transaction_data
        )
        if not response:
            return format_error("Unable to update transaction.")
        return json.dumps(response)

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
    async def get_transactions(
        budget_id: str, category_id: str, start_date: str
    ) -> str:
        """Fetch transactions from YNAB API
        Args:
            budget_id (str): The ID of the budget.
            category_id (str): The ID of the category.
            start_date (str): The start date in YYYY-MM-DD format.
        """
        response = await ynab_get(
            f"/budgets/{budget_id}/categories/{category_id}/transactions?since={start_date}"
        )
        if not response:
            return format_error("Unable to fetch transactions.", response)
        if not "transactions" in response:
            return format_error("No transactions found in response", response)
        transactions = response["transactions"]
        return format_transactions(transactions)

    @mcp.tool()
    async def get_transactions_for_account(
        budget_id: str, account_id: str, start_date: str
    ) -> str:
        """Fetch transactions for a specific account from YNAB API."""
        response = await ynab_get(
            f"/budgets/{budget_id}/accounts/{account_id}/transactions?since={start_date}"
        )
        if not response:
            return format_error("Unable to fetch transactions.", response)
        if not "transactions" in response:
            return format_error("No transactions found in response", response)
        transactions = response["transactions"]
        return format_transactions(transactions)

    @mcp.tool()
    async def get_transactions_for_month(budget_id: str, month: str) -> str:
        """Fetch transactions for a specific month from YNAB API."""
        response = await ynab_get(f"budgets/{budget_id}/months/{month}/transactions")
        if not response:
            return format_error("Unable to fetch transactions.", response)
        if not "transactions" in response:
            return format_error("No transactions found in response", response)
        transactions = response["transactions"]
        return format_transactions(transactions)
