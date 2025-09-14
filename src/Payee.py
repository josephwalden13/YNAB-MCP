from __future__ import annotations
from YNABClient import YNABClient
from AppContext import AppContext
from Budget import Budget
from mcp import ServerSession
from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel, Field


class Payee(BaseModel):
    id: str = Field()
    name: str | None = Field(default=None)
    transfer_account_id: str | None = Field(default=None)
    deleted: bool | None = Field(default=None)

    @staticmethod
    async def Get(
        ynab: YNABClient, budget: Budget | None = None
    ) -> list[Payee] | YNABClient.Error:
        budget_id = budget.id if budget else "last-used"
        url = f"/budgets/{budget_id}/payees"

        response = await ynab.Send(method="GET", path=url)
        if isinstance(response, YNABClient.Error):
            return response
        elif isinstance(response, YNABClient.Response):
            if "payees" in response.data:
                return [Payee(**x) for x in response.data["payees"]]
        raise YNABClient.Exceptions.UnexpectedError(
            "Unexpected response format. No payee data found."
        )

    @staticmethod
    def RegisterTools(mcp: FastMCP):
        """Register payee-related MCP tools."""

        @mcp.tool()
        async def get_payees(
            ctx: Context[ServerSession, AppContext], budget: Budget | None = None
        ) -> list[Payee] | YNABClient.Error:
            """Fetch payees from YNAB API."""
            client = ctx.request_context.lifespan_context.ynab
            return await Payee.Get(client, budget)
