from __future__ import annotations
from YNABClient import YNABClient
from AppContext import AppContext
from mcp import ServerSession
from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel, Field


class Budget(BaseModel):
    id: str = Field(default="last-used")
    name: str | None = Field(default=None)
    first_month: str | None = Field(default=None)
    last_month: str | None = Field(default=None)

    @staticmethod
    async def Get(ynab: YNABClient) -> list[Budget] | YNABClient.Error:
        response = await ynab.Send("GET", "/budgets")

        if isinstance(response, YNABClient.Error):
            return response
        elif isinstance(response, YNABClient.Response):
            if "budgets" in response.data:
                return [Budget(**x) for x in response.data["budgets"]]
        raise YNABClient.Exceptions.UnexpectedError(
            "Unexpected response format. No budget data found."
        )

    @staticmethod
    def RegisterTools(mcp: FastMCP):
        """Register budget-related MCP tools."""

        @mcp.tool()
        async def get_budgets(
            ctx: Context[ServerSession, AppContext],
        ) -> list[Budget] | YNABClient.Error:
            """Fetch budgets from YNAB API."""
            client = ctx.request_context.lifespan_context.ynab
            return await Budget.Get(ynab=client)
