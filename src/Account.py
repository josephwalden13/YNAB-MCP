from __future__ import annotations

from pydantic import BaseModel, Field, computed_field
from YNABClient import YNABClient
from AppContext import AppContext
from Budget import Budget
from mcp import ServerSession
from mcp.server.fastmcp import Context, FastMCP


class Account(BaseModel):
    id: str = Field()
    name: str | None = Field(default=None)
    type: str | None = Field(default=None)
    on_budget: bool | None = Field(default=None)
    closed: bool | None = Field(default=None)
    note: str | None = Field(default=None)
    balance: int | None = Field(default=None)
    cleared_balance: int | None = Field(default=None)
    uncleared_balance: int | None = Field(default=None)
    transfer_payee_id: str | None = Field(default=None)
    last_reconciled_at: str | None = Field(default=None)
    debt_original_balance: int | None = Field(default=None)
    debt_interest_rates: dict[str, int] | None = Field(default=None)
    debt_minimum_payments: dict[str, int] | None = Field(default=None)
    debt_escrow_amounts: dict[str, int] | None = Field(default=None)
    deleted: bool | None = Field(default=None)

    @computed_field
    @property
    def balance_in_currency(self) -> float | None:
        """Convert balance from milliunits to standard currency format."""
        if self.balance is not None:
            return self.balance / 1000.0
        return None

    @computed_field
    @property
    def cleared_balance_in_currency(self) -> float | None:
        """Convert cleared_balance from milliunits to standard currency format."""
        if self.cleared_balance is not None:
            return self.cleared_balance / 1000.0
        return None

    @computed_field
    @property
    def uncleared_balance_in_currency(self) -> float | None:
        """Convert uncleared_balance from milliunits to standard currency format."""
        if self.uncleared_balance is not None:
            return self.uncleared_balance / 1000.0
        return None

    @computed_field
    @property
    def debt_interest_rates_in_percentage(self) -> dict[str, float] | None:
        """Convert debt_interest_rates from milliunits points to percentage format."""
        if self.debt_interest_rates is not None:
            return {k: v / 1000.0 for k, v in self.debt_interest_rates.items()}
        return None

    @computed_field
    @property
    def debt_minimum_payments_in_currency(self) -> dict[str, float] | None:
        """Convert debt_minimum_payments from milliunits to standard currency format."""
        if self.debt_minimum_payments is not None:
            return {k: v / 1000.0 for k, v in self.debt_minimum_payments.items()}
        return None

    @computed_field
    @property
    def debt_escrow_amounts_in_currency(self) -> dict[str, float] | None:
        """Convert debt_escrow_amounts from milliunits to standard currency format."""
        if self.debt_escrow_amounts is not None:
            return {k: v / 1000.0 for k, v in self.debt_escrow_amounts.items()}
        return None

    @staticmethod
    async def Get(ynab: YNABClient, budget: Budget) -> list[Account] | YNABClient.Error:
        response = await ynab.Send(method="GET", path=f"/budgets/{budget.id}/accounts")
        if isinstance(response, YNABClient.Error):
            return response
        elif isinstance(response, YNABClient.Response):
            if "accounts" in response.data:
                return [Account(**account) for account in response.data["accounts"]]
        raise YNABClient.Exceptions.UnexpectedError(
            "Unexpected response format. No transaction data found."
        )

    @staticmethod
    def RegisterTools(mcp: FastMCP):
        """Register account-related MCP tools."""

        @mcp.tool()
        async def get_accounts(
            ctx: Context[ServerSession, AppContext], budget: Budget
        ) -> list[Account] | YNABClient.Error:
            """Fetch accounts from YNAB API."""
            client = ctx.request_context.lifespan_context.ynab
            return await Account.Get(ynab=client, budget=budget)
