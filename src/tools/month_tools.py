import json
from json import dumps
from typing import Any
from mcp.server.fastmcp import FastMCP
from tools.api_client import GetError, ynab_get, ynab_put


class Month:
    month: str | None
    note: str | None
    income: float | None
    budgeted: float | None
    activity: float | None
    to_be_budgeted: float | None
    age_of_money: int | None
    deleted: bool | None

    def __init__(self, json: dict[str, Any]):
        self.month = json.get("month")
        self.note = json.get("note")
        self.income = (json["income"] or 0) / 1000 if json.get("income") is not None else None
        self.budgeted = (json["budgeted"] or 0) / 1000 if json.get("budgeted") is not None else None
        self.activity = (json["activity"] or 0) / 1000 if json.get("activity") is not None else None
        self.to_be_budgeted = (json["to_be_budgeted"] or 0) / 1000 if json.get("to_be_budgeted") is not None else None
        self.age_of_money = json.get("age_of_money")
        self.deleted = json.get("deleted")

    def toJson(self) -> dict[str, Any]:
        json = {
            "month": self.month,
            "note": self.note,
            "income": self.income,
            "budgeted": self.budgeted,
            "activity": self.activity,
            "to_be_budgeted": self.to_be_budgeted,
            "age_of_money": self.age_of_money,
            "deleted": self.deleted,
        }
        return {x: json[x] for x in json if json[x] is not None}


async def _get_months(budget_id: str = "last-used") -> list[Month]:
    response = await ynab_get(f"/budgets/{budget_id}/months")
    if not response:
        raise GetError({"error": "Unable to fetch months.", "response": response})
    if not "months" in response:
        raise GetError(
            {"error": "No months found in response", "response": response}
        )
    months = [Month(x) for x in response["months"]]
    return months


def register_month_tools(mcp: FastMCP):
    """Register month-related MCP tools."""

    @mcp.tool()
    async def get_months(budget_id: str = "last-used") -> str:
        """Fetch months from YNAB API.
        Args:
            budget_id (str, optional): The ID of the budget. If not provided the last used budget will be used.
        """
        months = await _get_months(budget_id)
        return dumps([x.toJson() for x in months])
