from __future__ import annotations
from YNABClient import YNABClient
from AppContext import AppContext
from Budget import Budget
from mcp import ServerSession
from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel, Field


class Month(BaseModel):
    month: str = Field(default="current")
    note: str | None = Field(default=None)
    income: float | None = Field(default=None)
    budgeted: float | None = Field(default=None)
    activity: float | None = Field(default=None)
    to_be_budgeted: float | None = Field(default=None)
    age_of_money: int | None = Field(default=None)
    deleted: bool | None = Field(default=None)

    @staticmethod
    async def Get(
        ynab: YNABClient, budget: Budget | None = None
    ) -> list[Month] | YNABClient.Error:
        response = await ynab.Send(
            method="GET",
            path=f"/budgets/{budget.__getattribute__('id') or 'last-used'}/months",
        )
        if isinstance(response, YNABClient.Error):
            return response
        elif isinstance(response, YNABClient.Response):
            if "months" in response.data:
                return [Month(**month) for month in response.data["months"]]
        raise YNABClient.Exceptions.UnexpectedError(
            "Unexpected response format. No transaction data found."
        )

    @staticmethod
    def RegisterTools(mcp: FastMCP):
        """Register month-related MCP tools."""

        @mcp.tool()
        async def get_months(
            ctx: Context[ServerSession, AppContext], budget: Budget | None = None
        ) -> list[Month] | YNABClient.Error:
            """Fetch months from YNAB API."""
            client = ctx.request_context.lifespan_context.ynab
            return await Month.Get(client, budget)
