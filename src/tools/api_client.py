import httpx
import os
from typing import Any

# Constants
YNAB_API_BASE = "https://api.ynab.com/v1"
YNAB_API_TOKEN = os.environ.get("YNAB_API_TOKEN")

assert YNAB_API_TOKEN, "Missing YNAB_API_TOKEN environment variable"


async def ynab_get(url: str) -> dict[str, Any] | None:
    """Fetch all budgets from YNAB API."""
    headers = {
        "Authorization": f"Bearer {YNAB_API_TOKEN}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{YNAB_API_BASE}/{url}", headers=headers)
            response.raise_for_status()
            response_json = response.json()
            if not "data" in response_json:
                return None
            return response_json["data"]
        except Exception as e:
            return None


async def ynab_post(url: str, data: dict[str, Any]) -> dict[str, Any] | None:
    """Create a resource in YNAB API."""
    headers = {
        "Authorization": f"Bearer {YNAB_API_TOKEN}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{YNAB_API_BASE}/{url}", headers=headers, json=data
            )
            response.raise_for_status()
            response_json = response.json()
            if not "data" in response_json:
                raise ValueError(f"Invalid response: {response_json}")
            return response_json["data"]
        except Exception as e:
            return {"error": str(e), "data": data}


async def ynab_put(url: str, data: dict[str, Any]) -> dict[str, Any] | None:
    """Update a resource in YNAB API."""
    headers = {
        "Authorization": f"Bearer {YNAB_API_TOKEN}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(
                f"{YNAB_API_BASE}/{url}", headers=headers, json=data
            )
            response.raise_for_status()
            response_json = response.json()
            if not "data" in response_json:
                raise ValueError(f"Invalid response: {response_json}")
            return response_json["data"]
        except Exception as e:
            return {"error": str(e), "data": data}


async def ynab_delete(url: str) -> dict[str, Any] | None:
    """Delete a resource in YNAB API."""
    headers = {
        "Authorization": f"Bearer {YNAB_API_TOKEN}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(f"{YNAB_API_BASE}/{url}", headers=headers)
            response.raise_for_status()
            response_json = response.json()
            return response_json
        except Exception as e:
            return None
