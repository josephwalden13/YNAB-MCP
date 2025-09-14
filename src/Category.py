from __future__ import annotations
from YNABClient import YNABClient
from AppContext import AppContext
from Budget import Budget
from mcp import ServerSession
from mcp.server.fastmcp import Context, FastMCP
from Month import Month
from pydantic import BaseModel, Field, computed_field


class Category(BaseModel):
    id: str = Field()
    category_group_id: str | None = Field(default=None)
    category_group_name: str | None = Field(default=None)
    name: str | None = Field(default=None)
    hidden: bool | None = Field(default=None)
    original_category_group_id: str | None = Field(default=None)
    note: str | None = Field(default=None)
    budgeted: int | None = Field(default=None)
    activity: int | None = Field(default=None)
    balance: int | None = Field(default=None)
    goal_type: str | None = Field(default=None)
    goal_needs_whole_amount: bool | None = Field(default=None)
    goal_day: int | None = Field(default=None)
    goal_cadence: int | None = Field(default=None)
    goal_cadence_frequency: int | None = Field(default=None)
    goal_creation_month: str | None = Field(default=None)
    goal_target: int | None = Field(default=None)
    goal_target_month: str | None = Field(default=None)
    goal_percentage_complete: int | None = Field(default=None)
    goal_months_to_budget: int | None = Field(default=None)
    goal_under_funded: int | None = Field(default=None)
    goal_overall_funded: int | None = Field(default=None)
    goal_overall_left: int | None = Field(default=None)
    goal_snoozed_at: str | None = Field(default=None)
    deleted: bool | None = Field(default=None)

    @computed_field
    @property
    def budgeted_in_currency(self) -> float | None:
        if self.budgeted is not None:
            return self.budgeted / 1000.0
        return None

    @computed_field
    @property
    def activity_in_currency(self) -> float | None:
        if self.activity is not None:
            return self.activity / 1000.0
        return None

    @computed_field
    @property
    def balance_in_currency(self) -> float | None:
        if self.balance is not None:
            return self.balance / 1000.0
        return None

    @computed_field
    @property
    def goal_target_in_currency(self) -> float | None:
        if self.goal_target is not None:
            return self.goal_target / 1000.0
        return None

    @computed_field
    @property
    def goal_under_funded_in_currency(self) -> float | None:
        if self.goal_under_funded is not None:
            return self.goal_under_funded / 1000.0
        return None

    @computed_field
    @property
    def goal_overall_funded_in_currency(self) -> float | None:
        if self.goal_overall_funded is not None:
            return self.goal_overall_funded / 1000.0
        return None

    @computed_field
    @property
    def goal_overall_left_in_currency(self) -> float | None:
        if self.goal_overall_left is not None:
            return self.goal_overall_left / 1000.0
        return None

    @staticmethod
    async def Get(
        ynab: YNABClient,
        budget: Budget | None = None,
        month: Month | None = None,
        category: Category | None = None,
    ) -> list[Category] | Category | YNABClient.Error:
        budget_id = budget.id if budget else "last-used"

        url: str = str()
        if month and category:
            url = f"/budgets/{budget_id}/months/{month.month}/categories/{category.id}"
        else:
            url = f"/budgets/{budget_id}/categories"

        response = await ynab.Send(method="GET", path=url)
        if isinstance(response, YNABClient.Error):
            return response
        elif isinstance(response, YNABClient.Response):
            if "category" in response.data:
                return Category(**response.data["category"])
            elif "category_groups" in response.data:
                return [
                    Category(**category)
                    for group in response.data["category_groups"]
                    for category in group["categories"]
                ]
            elif "categories" in response.data:
                return [
                    Category(**category) for category in response.data["categories"]
                ]
        raise YNABClient.Exceptions.UnexpectedError(
            "Unexpected response format. No transaction data found."
        )

    @staticmethod
    async def Update(
        ynab: YNABClient,
        category: Category,
        budget: Budget | None = None,
        month: Month | None = None,
    ) -> Category | YNABClient.Error:
        budget_id: str
        if budget:
            budget_id = budget.id
        else:
            budget_id = "last-used"

        url: str
        if month:
            url = f"/budgets/{budget_id}/months/{month.month}/categories/{category.id}"
        else:
            url = f"/budgets/{budget_id}/categories/{category.id}"

        response = await ynab.Send(
            method="PUT",
            path=url,
            json=category.model_dump(exclude_unset=True),
        )
        if isinstance(response, YNABClient.Error):
            return response
        elif isinstance(response, YNABClient.Response):
            if "category" in response.data:
                return Category(**response.data["category"])
        raise YNABClient.Exceptions.UnexpectedError(
            "Unexpected response format. No transaction data found."
        )

    @staticmethod
    def RegisterTools(mcp: FastMCP):
        """Register category-related MCP tools."""

        @mcp.tool()
        async def get_categories(
            ctx: Context[ServerSession, AppContext], budget: Budget | None = None
        ) -> Category | list[Category] | YNABClient.Error:
            """Fetch categories from YNAB API."""
            client = ctx.request_context.lifespan_context.ynab
            return await Category.Get(ynab=client, budget=budget)

        @mcp.tool()
        async def get_category_for_month(
            ctx: Context[ServerSession, AppContext],
            budget: Budget | None = None,
            month: Month | None = None,
            category: Category | None = None,
        ) -> Category | list[Category] | YNABClient.Error:
            """Fetch categories for a specific month from YNAB API."""
            client = ctx.request_context.lifespan_context.ynab
            return await Category.Get(
                ynab=client, budget=budget, month=month, category=category
            )

        @mcp.tool()
        async def update_category(
            ctx: Context[ServerSession, AppContext],
            category: Category,
            budget: Budget | None = None,
        ) -> Category | YNABClient.Error:
            """Update a category in YNAB API."""
            client = ctx.request_context.lifespan_context.ynab
            return await Category.Update(client, category, budget=budget)

        @mcp.tool()
        async def update_category_for_month(
            ctx: Context[ServerSession, AppContext],
            category: Category,
            budget: Budget | None = None,
            month: Month | None = None,
        ) -> Category | YNABClient.Error:
            """Update a category for a specific month in YNAB API."""
            client = ctx.request_context.lifespan_context.ynab
            return await Category.Update(
                ynab=client, category=category, budget=budget, month=month
            )
