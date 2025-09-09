import json
from json import dumps
from typing import Any
from mcp.server.fastmcp import FastMCP
from tools.api_client import GetError, ynab_get


class Payee:
    id: str | None
    name: str | None
    transfer_account_id: str | None
    deleted: bool | None

    def __init__(self, json: dict[str, Any]):
        self.id = json.get("id")
        self.name = json.get("name")
        self.transfer_account_id = json.get("transfer_account_id")
        self.deleted = json.get("deleted")

    def toJson(self) -> dict[str, Any]:
        json = {
            "id": self.id,
            "name": self.name,
            "transfer_account_id": self.transfer_account_id,
            "deleted": self.deleted,
        }
        return {x: json[x] for x in json if json[x] is not None}


async def _get_payees(budget_id: str = "last-used") -> list[Payee]:
    response = await ynab_get(f"/budgets/{budget_id}/payees")
    if not response:
        raise GetError({"error": "Unable to fetch payees.", "response": response})
    if not "payees" in response:
        raise GetError(
            {"error": "No payees found in response", "response": response}
        )
    payees = [Payee(x) for x in response["payees"]]
    return payees


def register_payee_tools(mcp: FastMCP):
    """Register payee-related MCP tools."""

    @mcp.tool()
    async def get_payees(budget_id: str = "last-used") -> str:
        """Fetch payees from YNAB API.
        Args:
            budget_id (str, optional): The ID of the budget. If not provided the last used budget will be used.
        """
        payees = await _get_payees(budget_id)
        return dumps([x.toJson() for x in payees])
