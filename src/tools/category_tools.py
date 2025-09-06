import json
from mcp.server.fastmcp import FastMCP
from .api_client import format_error, ynab_get, ynab_put


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


def register_category_tools(mcp: FastMCP):
    """Register category-related MCP tools."""

    @mcp.tool()
    async def get_categories(budget_id: str) -> str:
        """Fetch categories from YNAB API."""
        response = await ynab_get(f"budgets/{budget_id}/categories")
        if not response:
            return format_error("Unable to fetch categories.")
        if not "category_groups" in response:
            return format_error("No category groups found in response.", response=response)
        category_groups = response["category_groups"]
        categories = [
            category for group in category_groups for category in group["categories"]
        ]
        return format_categories(categories)

    @mcp.tool()
    async def get_categories_for_month(
        budget_id: str, month: str, category_id: str
    ) -> str:
        """Fetch categories for a specific month from YNAB API."""
        response = await ynab_get(
            f"budgets/{budget_id}/months/{month}/categories/{category_id}"
        )
        if not response:
            return format_error("Unable to fetch category.")
        if not "category" in response:
            return format_error("No category found in response.", response=response)
        category = response["category"]
        return format_categories([category])

    @mcp.tool()
    async def update_category(
        budget_id: str,
        category_id: str,
        name: str | None = None,
        note: str | None = None,
        goal_target: int | None = None,
    ) -> str:
        """Update a category in YNAB API."""
        category = {}
        if name is not None:
            category["name"] = name
        if note is not None:
            category["note"] = note
        if goal_target is not None:
            category["goal_target"] = goal_target
        category_data = {"category": category}

        response = await ynab_put(
            f"budgets/{budget_id}/categories/{category_id}", category_data
        )
        if not response:
            return format_error("Unable to update category.")
        return json.dumps(response)

    @mcp.tool()
    async def update_category_for_month(
        budget_id: str, month: str, category_id: str, budgeted: int
    ) -> str:
        """Update a category for a specific month in YNAB API."""
        category_data = {
            "category": {
                "budgeted": budgeted,
            }
        }
        response = await ynab_put(
            f"budgets/{budget_id}/months/{month}/categories/{category_id}",
            category_data,
        )
        if not response:
            return format_error("Unable to update category for month.")
        return json.dumps(response)
