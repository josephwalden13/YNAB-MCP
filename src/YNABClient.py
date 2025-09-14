from __future__ import annotations
from httpx import AsyncClient, Request, Response
from pydantic import BaseModel
from typing import Any
import os


class YNABClient:
    _YNAB_API_BASE = "https://api.ynab.com/v1"
    _api_token: str

    class Exceptions:
        class UnexpectedError(Exception):
            pass

    class Response(BaseModel):
        data: dict[str, Any]

        @classmethod
        def from_JSON(cls, response_json: dict[str, Any]) -> YNABClient.Response:
            return cls(data=response_json.get("data", {}))

    class Error(BaseModel):
        id: str
        name: str
        detail: str

        @classmethod
        def from_JSON(cls, response_json: dict[str, Any]) -> YNABClient.Error:
            error = response_json.get("error", {})
            return cls(
                id=error.get("id", ""),
                name=error.get("name", ""),
                detail=error.get("detail", ""),
            )

    def __init__(self, api_token: str | None = None) -> None:
        if api_token:
            self._api_token = api_token
            return
        environment_token: str | None = os.environ.get("YNAB_API_TOKEN")
        if not environment_token:
            raise ValueError("Missing YNAB_API_TOKEN environment variable")
        self._api_token = environment_token

    def _get_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_token}",
            "Content-Type": "application/json",
        }

    async def Send(
        self, method: str, path: str, json: dict[str, Any] | None = None
    ) -> YNABClient.Response | Error:
        """Send request to YNAB API."""
        url: str = f'{self._YNAB_API_BASE}/{path.strip("/")}'
        async with AsyncClient() as client:
            request: Request = client.build_request(
                method, url, headers=self._get_headers(), json=json
            )
            response: Response = await client.send(request)
            response_json: dict[str, Any] = response.json()
            if response.is_success:
                return YNABClient.Response.from_JSON(response_json)
            elif "error" in response_json:
                return YNABClient.Error.from_JSON(response_json)
            response.raise_for_status()
            raise YNABClient.Exceptions.UnexpectedError(
                f"Unexpected error: {response_json}"
            )
