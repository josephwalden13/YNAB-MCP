import json
from json import dumps
from typing import Any
from mcp.server.fastmcp import FastMCP
from tools.api_client import GetError, PutError, ynab_get, ynab_put


class Category:
    id: str | None
    category_group_id: str | None
    category_group_name: str | None
    name: str | None
    hidden: bool | None
    original_category_group_id: str | None
    note: str | None
    budgeted: float | None
    activity: float | None
    balance: float | None
    goal_type: str | None
    goal_needs_whole_amount: bool | None
    goal_day: int | None
    goal_cadence: int | None
    goal_cadence_frequency: int | None
    goal_creation_month: str | None
    goal_target: float | None
    goal_target_month: str | None
    goal_percentage_complete: int | None
    goal_months_to_budget: int | None
    goal_under_funded: float | None
    goal_overall_funded: float | None
    goal_overall_left: float | None
    goal_snoozed_at: str | None
    deleted: bool | None

    def __init__(self, json: dict[str, Any]):
        self.id = json.get("id")
        self.category_group_id = json.get("category_group_id")
        self.category_group_name = json.get("category_group_name")
        self.name = json.get("name")
        self.hidden = json.get("hidden")
        self.original_category_group_id = json.get("original_category_group_id")
        self.note = json.get("note")
        self.budgeted = (json["budgeted"] or 0) / 1000 if json.get("budgeted") is not None else None
        self.activity = (json["activity"] or 0) / 1000 if json.get("activity") is not None else None
        self.balance = (json["balance"] or 0) / 1000 if json.get("balance") is not None else None
        self.goal_type = json.get("goal_type")
        self.goal_needs_whole_amount = json.get("goal_needs_whole_amount")
        self.goal_day = json.get("goal_day")
        self.goal_cadence = json.get("goal_cadence")
        self.goal_cadence_frequency = json.get("goal_cadence_frequency")
        self.goal_creation_month = json.get("goal_creation_month")
        self.goal_target = (json["goal_target"] or 0) / 1000 if json.get("goal_target") is not None else None
        self.goal_target_month = json.get("goal_target_month")
        self.goal_percentage_complete = json.get("goal_percentage_complete")
        self.goal_months_to_budget = json.get("goal_months_to_budget")
        self.goal_under_funded = (json["goal_under_funded"] or 0) / 1000 if json.get("goal_under_funded") is not None else None
        self.goal_overall_funded = (json["goal_overall_funded"] or 0) / 1000 if json.get("goal_overall_funded") is not None else None
        self.goal_overall_left = (json["goal_overall_left"] or 0) / 1000 if json.get("goal_overall_left") is not None else None
        self.goal_snoozed_at = json.get("goal_snoozed_at")
        self.deleted = json.get("deleted")

    def toJson(self) -> dict[str, Any]:
        json = {
            "id": self.id,
            "category_group_id": self.category_group_id,
            "category_group_name": self.category_group_name,
            "name": self.name,
            "hidden": self.hidden,
            "original_category_group_id": self.original_category_group_id,
            "note": self.note,
            "budgeted": self.budgeted,
            "activity": self.activity,
            "balance": self.balance,
            "goal_type": self.goal_type,
            "goal_needs_whole_amount": self.goal_needs_whole_amount,
            "goal_day": self.goal_day,
            "goal_cadence": self.goal_cadence,
            "goal_cadence_frequency": self.goal_cadence_frequency,
            "goal_creation_month": self.goal_creation_month,
            "goal_target": self.goal_target,
            "goal_target_month": self.goal_target_month,
            "goal_percentage_complete": self.goal_percentage_complete,
            "goal_months_to_budget": self.goal_months_to_budget,
            "goal_under_funded": self.goal_under_funded,
            "goal_overall_funded": self.goal_overall_funded,
            "goal_overall_left": self.goal_overall_left,
            "goal_snoozed_at": self.goal_snoozed_at,
            "deleted": self.deleted,
        }
        return {x: json[x] for x in json if json[x] is not None}


async def _get_categories(budget_id: str = "last-used") -> list[Category]:
    response = await ynab_get(f"/budgets/{budget_id}/categories")
    if not response:
        raise GetError({"error": "Unable to fetch categories.", "response": response})
    if not "category_groups" in response:
        raise GetError(
            {"error": "No category groups found in response", "response": response}
        )
    category_groups = response["category_groups"]
    categories = [
        Category(category) for group in category_groups for category in group["categories"]
    ]
    return categories


async def _get_category_for_month(
    budget_id: str, month: str, category_id: str
) -> Category:
    response = await ynab_get(
        f"/budgets/{budget_id}/months/{month}/categories/{category_id}"
    )
    if not response:
        raise GetError({"error": "Unable to fetch category.", "response": response})
    if not "category" in response:
        raise GetError(
            {"error": "No category found in response", "response": response}
        )
    return Category(response["category"])


async def _update_category(
    budget_id: str,
    category_id: str,
    name: str | None = None,
    note: str | None = None,
    goal_target: int | None = None,
) -> dict[str, Any]:
    category = {}
    if name is not None:
        category["name"] = name
    if note is not None:
        category["note"] = note
    if goal_target is not None:
        category["goal_target"] = goal_target
    category_data = {"category": category}

    response = await ynab_put(
        f"/budgets/{budget_id}/categories/{category_id}", category_data
    )
    if not response:
        raise PutError({"error": "Unable to update category.", "response": response})
    return response


async def _update_category_for_month(
    budget_id: str, month: str, category_id: str, budgeted: int
) -> dict[str, Any]:
    category_data = {
        "category": {
            "budgeted": budgeted,
        }
    }
    response = await ynab_put(
        f"/budgets/{budget_id}/months/{month}/categories/{category_id}",
        category_data,
    )
    if not response:
        raise PutError({"error": "Unable to update category for month.", "response": response})
    return response


def register_category_tools(mcp: FastMCP):
    """Register category-related MCP tools."""

    @mcp.tool()
    async def get_categories(budget_id: str = "last-used") -> str:
        """Fetch categories from YNAB API.
        Args:
            budget_id (str, optional): The ID of the budget. If not provided the last used budget will be used.
        """
        categories = await _get_categories(budget_id)
        return dumps([x.toJson() for x in categories])

    @mcp.tool()
    async def get_categories_for_month(
        budget_id: str, month: str, category_id: str
    ) -> str:
        """Fetch categories for a specific month from YNAB API.
        Args:
            budget_id (str): The ID of the budget.
            month (str): The month in YYYY-MM-DD format.
            category_id (str): The ID of the category.
        """
        category = await _get_category_for_month(budget_id, month, category_id)
        return json.dumps(category.toJson())

    @mcp.tool()
    async def update_category(
        budget_id: str,
        category_id: str,
        name: str | None = None,
        note: str | None = None,
        goal_target: int | None = None,
    ) -> str:
        """Update a category in YNAB API.
        Args:
            budget_id (str): The ID of the budget.
            category_id (str): The ID of the category.
            name (str, optional): The new name for the category.
            note (str, optional): The new note for the category.
            goal_target (int, optional): The new goal target in milliunits.
        """
        response = await _update_category(budget_id, category_id, name, note, goal_target)
        return json.dumps(response)

    @mcp.tool()
    async def update_category_for_month(
        budget_id: str, month: str, category_id: str, budgeted: int
    ) -> str:
        """Update a category for a specific month in YNAB API.
        Args:
            budget_id (str): The ID of the budget.
            month (str): The month in YYYY-MM-DD format.
            category_id (str): The ID of the category.
            budgeted (int): The amount budgeted in milliunits.
        """
        response = await _update_category_for_month(budget_id, month, category_id, budgeted)
        return json.dumps(response)
