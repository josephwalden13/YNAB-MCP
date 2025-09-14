from __future__ import annotations
from Account import Account
from Budget import Budget
from Category import Category
from Month import Month
from YNABClient import YNABClient
from AppContext import AppContext
from mcp import ServerSession
from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel, Field, computed_field
from typing import Any

from Payee import Payee


class Transaction(BaseModel):
    """
    Transaction Object from YNAB API v1.
    Important to note: Amounts are in milliunits. For example, $1.00 is represented as 1000.
    """

    id: str | None = Field(default=None)
    account_id: str | None = Field(default=None)
    amount: int | None = Field(default=None, description="Amount in milliunits")
    approved: bool | None = Field(default=None)
    cleared: str | None = Field(
        default=None, pattern=r"^(cleared|uncleared|reconciled)$"
    )
    date: str | None = Field(default=None)
    deleted: bool | None = Field(default=None)
    # flag_color:
    #     $ref: "#/components/schemas/TransactionFlagColor"
    # flag_name:
    #     $ref: "#/components/schemas/TransactionFlagName"
    memo: str | None = Field(default=None)
    payee_id: str | None = Field(default=None)
    category_id: str | None = Field(default=None)
    transfer_account_id: str | None = Field(default=None)
    transfer_transaction_id: str | None = Field(default=None)
    matched_transaction_id: str | None = Field(default=None)
    import_id: str | None = Field(default=None)
    import_payee_name: str | None = Field(default=None)
    import_payee_name_original: str | None = Field(default=None)
    debt_transaction_type: str | None = Field(default=None)

    @computed_field
    @property
    def amount_in_currency(self) -> float | None:
        """Convert amount from milliunits to standard currency format."""
        if self.amount is not None:
            return self.amount / 1000.0
        return None

    @staticmethod
    async def Get(
        ynab: YNABClient,
        budget: Budget | None = None,
        transaction: Transaction | None = None,
        category: Category | None = None,
        account: Account | None = None,
        month: Month | None = None,
        payee: Payee | None = None,
        since: str | None = None,
    ) -> Transaction | list[Transaction] | YNABClient.Error:
        budget_id = budget.id if budget else "last-used"
        url: str
        if transaction:
            url = f"/budgets/{budget_id}/transactions/{transaction.id}"
        elif category:
            url = f"/budgets/{budget_id}/categories/{category.id}/transactions"
        elif account:
            url = f"/budgets/{budget_id}/accounts/{account.id}/transactions"
        elif month:
            url = f"/budgets/{budget_id}/months/{month.month}/transactions"
        elif payee:
            url = f"/budgets/{budget_id}/payees/{payee.id}/transactions"
        else:
            url = f"/budgets/{budget_id}/transactions"

        if since:
            url += f"?since={since}"

        response = await ynab.Send(method="GET", path=url)
        if isinstance(response, YNABClient.Error):
            return response
        elif isinstance(response, YNABClient.Response):
            if "transaction" in response.data:
                return Transaction(**response.data["transaction"])
            elif "transactions" in response.data:
                return [Transaction(**x) for x in response.data["transactions"]]
        raise YNABClient.Exceptions.UnexpectedError(
            "Unexpected response format. No transaction data found."
        )

    async def Delete(
        self,
        ynab: YNABClient,
        budget_id: str | None = "last-used",
    ) -> Transaction | YNABClient.Error:
        url = f"/budgets/{budget_id}/transactions/{self.id}"

        response = await ynab.Send(method="DELETE", path=url)
        if isinstance(response, YNABClient.Error):
            return response
        elif isinstance(response, YNABClient.Response):
            if "transaction" in response.data:
                return Transaction(**response.data["transaction"])
        raise YNABClient.Exceptions.UnexpectedError(
            "Unexpected response format. No transaction data found."
        )

    async def Update(
        self, ynab: YNABClient, budget_id: str = "last-used"
    ) -> Transaction | YNABClient.Error:
        url = f"/budgets/{budget_id}/transactions/{self.id}"

        response = await ynab.Send(
            method="PUT",
            path=url,
            json={"transaction": self.model_dump(exclude_unset=True)},
        )
        if isinstance(response, YNABClient.Error):
            return response
        elif isinstance(response, YNABClient.Response):
            if "transaction" in response.data:
                return Transaction(**response.data["transaction"])
        raise YNABClient.Exceptions.UnexpectedError(
            "Unexpected response format. No transaction data found."
        )

    async def Create(
        self, ynab: YNABClient, budget_id: str = "last-used"
    ) -> Transaction | YNABClient.Error:
        url = f"/budgets/{budget_id}/transactions"

        response = await ynab.Send(
            method="POST",
            path=url,
            json={"transaction": self.model_dump(exclude_unset=True)},
        )
        if isinstance(response, YNABClient.Error):
            return response
        elif isinstance(response, YNABClient.Response):
            if "transaction" in response.data:
                return Transaction(**response.data["transaction"])
        raise YNABClient.Exceptions.UnexpectedError(
            "Unexpected response format. No transaction data found."
        )

    @staticmethod
    def RegisterTools(mcp: FastMCP):
        """Register transaction-related MCP tools."""

        @mcp.tool()
        async def new_transaction(
            ctx: Context[ServerSession, AppContext],
            transaction: Transaction,
            budget_id: str = "last-used",
        ) -> Transaction | YNABClient.Error:
            """Create a new transaction in YNAB API."""
            client = ctx.request_context.lifespan_context.ynab
            return await transaction.Create(ynab=client, budget_id=budget_id)

        @mcp.tool()
        async def update_transaction(
            ctx: Context[ServerSession, AppContext],
            updated_transaction: Transaction,
            budget_id: str = "last-used",
        ) -> Transaction | YNABClient.Error:
            """Update a transaction in YNAB API."""
            client = ctx.request_context.lifespan_context.ynab
            return await updated_transaction.Update(ynab=client, budget_id=budget_id)

        @mcp.tool()
        async def delete_transaction(
            ctx: Context[ServerSession, AppContext],
            transaction: Transaction,
            budget_id: str = "last-used",
        ) -> Transaction | YNABClient.Error:
            """Delete a transaction in YNAB API."""
            client = ctx.request_context.lifespan_context.ynab
            return await transaction.Delete(ynab=client, budget_id=budget_id)

        @mcp.tool()
        async def get_transactions_for_category(
            ctx: Context[ServerSession, AppContext],
            category: Category | None = None,
            budget: Budget | None = None,
            since: str | None = None,
        ) -> list[Transaction] | Transaction | YNABClient.Error:
            """Fetch transactions from YNAB API for a specific category."""
            client = ctx.request_context.lifespan_context.ynab
            return await Transaction.Get(
                ynab=client, budget=budget, category=category, since=since
            )

        @mcp.tool()
        async def get_transactions_for_account(
            ctx: Context[ServerSession, AppContext],
            account: Account | None = None,
            budget: Budget | None = None,
            since: str | None = None,
        ) -> list[Transaction] | Transaction | YNABClient.Error:
            """Fetch transactions for a specific account from YNAB API."""
            client = ctx.request_context.lifespan_context.ynab
            return await Transaction.Get(
                ynab=client, budget=budget, account=account, since=since
            )

        @mcp.tool()
        async def get_transactions_for_month(
            ctx: Context[ServerSession, AppContext],
            month: Month | None = None,
            budget: Budget | None = None,
        ) -> list[Transaction] | Transaction | YNABClient.Error:
            """Fetch transactions for a specific month from YNAB API."""
            client = ctx.request_context.lifespan_context.ynab
            return await Transaction.Get(ynab=client, budget=budget, month=month)

        @mcp.tool()
        async def get_transactions_for_payee(
            ctx: Context[ServerSession, AppContext],
            payee: Payee | None = None,
            budget: Budget | None = None,
            since: str | None = None,
        ) -> list[Transaction] | Transaction | YNABClient.Error:
            """Fetch transactions for a specific payee from YNAB API."""
            client = ctx.request_context.lifespan_context.ynab
            return await Transaction.Get(
                ynab=client, budget=budget, payee=payee, since=since
            )

        @mcp.tool()
        async def get_all_transactions(
            ctx: Context[ServerSession, AppContext],
            budget: Budget | None = None,
            since: str | None = None,
        ) -> list[Transaction] | Transaction | YNABClient.Error:
            """Fetch all transactions from YNAB API."""
            client = ctx.request_context.lifespan_context.ynab
            return await Transaction.Get(ynab=client, budget=budget, since=since)
