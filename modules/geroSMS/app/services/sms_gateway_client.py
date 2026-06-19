import base64
from typing import Any

import httpx

from app.dependencies import sms_config


class SMSGatewayClient:
    """Async client for android-sms-gateway 3rdparty API."""

    def __init__(self):
        self._base_url = sms_config.gateway_url.rstrip("/")
        self._api_prefix = sms_config.gateway_api_prefix.rstrip("/")
        self._username = sms_config.gateway_username
        self._password = sms_config.gateway_password
        basic = base64.b64encode(f"{self._username}:{self._password}".encode()).decode()
        self._basic_header = {"Authorization": f"Basic {basic}"}
        self._access_token: str | None = None
        self._jwt_tried = False

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict:
        if not self._jwt_tried:
            await self._try_jwt()
        headers = self._bearer_headers() if self._access_token else self._basic_header
        headers = {**headers, **kwargs.pop("extra_headers", {})}
        headers.setdefault("Content-Type", "application/json")
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.request(method, f"{self._base_url}{self._api_prefix}{path}", headers=headers, **kwargs)
                if resp.status_code == 401 and self._access_token:
                    self._access_token = None
                    headers = self._basic_header
                    resp = await client.request(method, f"{self._base_url}{self._api_prefix}{path}", headers=headers, **kwargs)
                resp.raise_for_status()
                data = resp.json()
                if isinstance(data, list):
                    return {"data": data}
                return data
            except httpx.HTTPStatusError as e:
                detail = e.response.text[:300]
                return {"error": f"Erreur API sms-gate {e.response.status_code}", "details": detail}
            except httpx.RequestError as e:
                return {"error": "Impossible de joindre le serveur sms-gate", "details": str(e)}

    def _bearer_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._access_token}"}

    async def _try_jwt(self) -> None:
        self._jwt_tried = True
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.post(
                    f"{self._base_url}{self._api_prefix}/3rdparty/v1/auth/token",
                    headers={**self._basic_header, "Content-Type": "application/json"},
                    json={"ttl": 3600, "scopes": ["messages:send", "messages:read", "messages:list", "devices:list"]},
                )
                if resp.status_code == 201:
                    data = resp.json()
                    self._access_token = data.get("access_token")
            except Exception:
                pass

    async def send_sms(
        self,
        phone_numbers: list[str],
        text: str,
        device_id: str | None = None,
        sim_number: int | None = None,
        priority: int = 0,
    ) -> dict:
        payload: dict[str, Any] = {
            "textMessage": {"text": text},
            "phoneNumbers": phone_numbers,
            "priority": priority,
        }
        if device_id:
            payload["deviceId"] = device_id
        if sim_number is not None:
            payload["simNumber"] = sim_number
        return await self._request("POST", "/3rdparty/v1/messages", json=payload)

    async def get_messages(
        self,
        page: int = 1,
        per_page: int = 20,
        status: str | None = None,
        device_id: str | None = None,
    ) -> dict:
        params: dict[str, Any] = {"page": page, "perPage": per_page}
        if status:
            params["status"] = status
        if device_id:
            params["deviceId"] = device_id
        data = await self._request("GET", "/3rdparty/v1/messages", params=params)
        return data

    async def get_message(self, message_id: str) -> dict:
        return await self._request("GET", f"/3rdparty/v1/messages/{message_id}")

    async def get_devices(self) -> dict:
        return await self._request("GET", "/3rdparty/v1/devices")

    async def health(self) -> dict:
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                resp = await client.get(f"{self._base_url}/health")
                return {"status": "ok"} if resp.status_code == 200 else {"status": "error", "code": resp.status_code}
            except Exception as e:
                return {"status": "error", "details": str(e)}
