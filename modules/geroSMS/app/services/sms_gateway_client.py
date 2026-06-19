import base64
import time
from typing import Any

import httpx

from app.dependencies import sms_config


class SMSGatewayClient:
    """Async client for android-sms-gateway 3rdparty API."""

    def __init__(self):
        self._base_url = sms_config.gateway_url.rstrip("/")
        self._username = sms_config.gateway_username
        self._password = sms_config.gateway_password
        self._scopes = sms_config.sms_scopes
        self._token_ttl = sms_config.token_ttl
        self._access_token: str | None = None
        self._refresh_token: str | None = None
        self._token_expires_at: float = 0

    async def _ensure_token(self) -> str:
        now = time.time()
        if self._access_token and now < self._token_expires_at - 60:
            return self._access_token
        if self._refresh_token:
            try:
                return await self._refresh()
            except Exception:
                pass
        return await self._generate()

    async def _generate(self) -> str:
        basic = base64.b64encode(f"{self._username}:{self._password}".encode()).decode()
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{self._base_url}/3rdparty/v1/auth/token",
                headers={
                    "Authorization": f"Basic {basic}",
                    "Content-Type": "application/json",
                },
                json={"ttl": self._token_ttl, "scopes": self._scopes},
            )
            resp.raise_for_status()
            data = resp.json()
            self._access_token = data["access_token"]
            self._refresh_token = data.get("refresh_token")
            self._token_expires_at = time.time() + self._token_ttl
            return self._access_token

    async def _refresh(self) -> str:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{self._base_url}/3rdparty/v1/auth/token/refresh",
                headers={
                    "Authorization": f"Bearer {self._refresh_token}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            self._access_token = data["access_token"]
            self._refresh_token = data.get("refresh_token", self._refresh_token)
            self._token_expires_at = time.time() + self._token_ttl
            return self._access_token

    async def _post(self, path: str, json: dict[str, Any]) -> dict:
        token = await self._ensure_token()
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.post(
                    f"{self._base_url}{path}",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                    json=json,
                )
                if resp.status_code == 401:
                    self._access_token = None
                    token = await self._ensure_token()
                    resp = await client.post(
                        f"{self._base_url}{path}",
                        headers={
                            "Authorization": f"Bearer {token}",
                            "Content-Type": "application/json",
                        },
                        json=json,
                    )
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as e:
                detail = e.response.text[:300]
                return {"error": f"Erreur API sms-gate {e.response.status_code}", "details": detail}
            except httpx.RequestError as e:
                return {"error": "Impossible de joindre le serveur sms-gate", "details": str(e)}

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> dict:
        token = await self._ensure_token()
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.get(
                    f"{self._base_url}{path}",
                    headers={"Authorization": f"Bearer {token}"},
                    params=params,
                )
                if resp.status_code == 401:
                    self._access_token = None
                    token = await self._ensure_token()
                    resp = await client.get(
                        f"{self._base_url}{path}",
                        headers={"Authorization": f"Bearer {token}"},
                        params=params,
                    )
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as e:
                detail = e.response.text[:300]
                return {"error": f"Erreur API sms-gate {e.response.status_code}", "details": detail}
            except httpx.RequestError as e:
                return {"error": "Impossible de joindre le serveur sms-gate", "details": str(e)}

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
        return await self._post("/3rdparty/v1/messages", payload)

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
        return await self._get("/3rdparty/v1/messages", params)

    async def get_message(self, message_id: str) -> dict:
        return await self._get(f"/3rdparty/v1/messages/{message_id}")

    async def get_devices(self) -> dict:
        return await self._get("/3rdparty/v1/devices")

    async def health(self) -> dict:
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                resp = await client.get(f"{self._base_url}/health")
                if resp.status_code == 200:
                    return {"status": "ok"}
                return {"status": "error", "code": resp.status_code}
            except Exception as e:
                return {"status": "error", "details": str(e)}
