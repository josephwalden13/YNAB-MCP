import httpx
import json
import os
from mcp.server.fastmcp import FastMCP
from typing import Any

# Initialize FastMCP server
mcp = FastMCP(
    "ynab",
    instructions="You are a virtual accountant connected to the YNAB API.",
)

# Constants
YNAB_API_BASE = "https://api.ynab.com/v1"
YNAB_API_TOKEN = os.environ["YNAB_API_TOKEN"]

assert YNAB_API_TOKEN, "Missing YNAB_API_TOKEN environment variable"


async def ynab_request(url: str) -> dict[str, Any] | None:
    """Fetch all budgets from YNAB API."""
    headers = {
        "Authorization": f"Bearer {YNAB_API_TOKEN}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{YNAB_API_BASE}/{url}", headers=headers)
            response.raise_for_status()
            response_json = response.json()
            if not "data" in response_json:
                return None
            return response_json["data"]
        except Exception as e:
            return None


def format_user(user):
    return json.dumps(
        {
            "id": user["id"],
        }
    )


@mcp.tool()
async def get_user() -> str:
    """Fetch user information from YNAB API."""
    response = await ynab_request("user")
    if not response:
        return "Unable to fetch user information."
    assert "user" in response, "No user found in response"
    user = response["user"]
    return format_user(user)


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


@mcp.tool()
async def get_budgets() -> str:
    """Fetch budgets from YNAB API."""
    response = await ynab_request("budgets")
    if not response:
        return "Unable to fetch budgets."
    assert "budgets" in response, "No budgets found in response"
    budgets = response["budgets"]
    return format_budgets(budgets)


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


@mcp.tool()
async def get_accounts(budget_id: str) -> str:
    """Fetch accounts from YNAB API."""
    response = await ynab_request(f"budgets/{budget_id}/accounts")
    if not response:
        return "Unable to fetch accounts."
    assert "accounts" in response, "No accounts found in response"
    accounts = response["accounts"]
    return format_accounts(accounts)


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


@mcp.tool()
async def get_months(budget_id: str) -> str:
    """Fetch months from YNAB API."""
    response = await ynab_request(f"budgets/{budget_id}/months")
    if not response:
        return "Unable to fetch months."
    assert "months" in response, "No months found in response"
    months = response["months"]
    return format_months(months)


@mcp.tool()
async def get_payees(budget_id: str) -> str:
    """Fetch payees from YNAB API."""
    response = await ynab_request(f"budgets/{budget_id}/payees")
    if not response:
        return "Unable to fetch payees."
    assert "payees" in response, "No payees found in response"
    payees = response["payees"]
    return str(payees)


def format_categories(categories):
    return json.dumps(
        [
            {
                "id": category["id"],
                "category_group_id": category["category_group_id"],
                "category_group_name": category["category_group_name"],
                "name": category["name"],
                "hidden": category["hidden"],
                "original_category_group_id": category["original_category_group_id"],
                "note": category["note"],
                "budgeted": (category["budgeted"] or 0) / 1000,
                "activity": (category["activity"] or 0) / 1000,
                "balance": (category["balance"] or 0) / 1000,
                "goal_type": category["goal_type"],
                "goal_needs_whole_amount": category["goal_needs_whole_amount"],
                "goal_day": category["goal_day"],
                "goal_cadence": category["goal_cadence"],
                "goal_cadence_frequency": category["goal_cadence_frequency"],
                "goal_creation_month": category["goal_creation_month"],
                "goal_target": (category["goal_target"] or 0) / 1000,
                "goal_target_month": category["goal_target_month"],
                "goal_percentage_complete": category["goal_percentage_complete"],
                "goal_months_to_budget": category["goal_months_to_budget"],
                "goal_under_funded": (category["goal_under_funded"] or 0) / 1000,
                "goal_overall_funded": (category["goal_overall_funded"] or 0) / 1000,
                "goal_overall_left": (category["goal_overall_left"] or 0) / 1000,
                "goal_snoozed_at": category["goal_snoozed_at"],
                "deleted": category["deleted"],
            }
            for category in categories
        ]
    )


@mcp.tool()
async def get_categories(budget_id: str) -> str:
    """Fetch categories from YNAB API."""
    response = await ynab_request(f"budgets/{budget_id}/categories")
    if not response:
        return "Unable to fetch categories."
    assert "category_groups" in response, "No category groups found in response"
    category_groups = response["category_groups"]
    categories = [
        category for group in category_groups for category in group["categories"]
    ]
    return format_categories(categories)


@mcp.tool()
async def get_categories_for_month(budget_id: str, month: str, category_id: str) -> str:
    """Fetch categories for a specific month from YNAB API."""
    response = await ynab_request(f"budgets/{budget_id}/months/{month}/categories/{category_id}")
    if not response:
        return "Unable to fetch categories."
    assert "category_groups" in response, "No category groups found in response"
    category_groups = response["category_groups"]
    categories = [
        category for group in category_groups for category in group["categories"]
    ]
    return format_categories(categories)


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


@mcp.tool()
async def get_transactions(budget_id: str, category_id: str, start_date: str) -> str:
    """Fetch transactions from YNAB API
    Args:
        budget_id (str): The ID of the budget.
        category_id (str): The ID of the category.
        start_date (str): The start date in YYYY-MM-DD format.
    """
    response = await ynab_request(
        f"/budgets/{budget_id}/categories/{category_id}/transactions?since={start_date}"
    )
    if not response:
        return "Unable to fetch transactions."
    assert "transactions" in response, "No transactions found in response"
    transactions = response["transactions"]
    return format_transactions(transactions)


@mcp.tool()
async def get_transactions_for_month(budget_id: str, month: str) -> str:
    """Fetch transactions for a specific month from YNAB API."""
    response = await ynab_request(f"budgets/{budget_id}/months/{month}/transactions")
    if not response:
        return "Unable to fetch transactions."
    assert "transactions" in response, "No transactions found in response"
    transactions = response["transactions"]
    return format_transactions(transactions)


@mcp.tool()
async def get_transactions_for_account(
    budget_id: str, account_id: str, start_date: str
) -> str:
    """Fetch transactions for a specific account from YNAB API."""
    response = await ynab_request(
        f"/budgets/{budget_id}/accounts/{account_id}/transactions?since={start_date}"
    )
    if not response:
        return "Unable to fetch transactions."
    assert "transactions" in response, "No transactions found in response"
    transactions = response["transactions"]
    return format_transactions(transactions)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
