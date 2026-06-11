import httpx
import os
from pathlib import Path
from typing import Any
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env", override=True)


class SupabaseClient:
    BASE_URL = "https://nhxzumcbqlyjumdirpax.supabase.co/rest/v1"

    def __init__(self, service_key: str):
        self._init_key = service_key

    def _key(self) -> str:
        return self._init_key or os.environ.get("SUPABASE_SERVICE_KEY", "")

    def _headers(self) -> dict[str, str]:
        k = self._key()
        return {
            "apikey": k,
            "Authorization": f"Bearer {k}",
            "Content-Type": "application/json",
        }

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> dict:
        key = self._key()
        if not key:
            return {"error": "SUPABASE_SERVICE_KEY manquante"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}{path}",
                    headers=self._headers(),
                    params=params,
                )
                response.raise_for_status()
                return {"data": response.json()}
            except Exception as e:
                return {"error": str(e)}

    async def search_contact(self, nom: str) -> list[dict]:
        result = await self._get("/interim_contact_information", {
            "select": "nom,prenom,mail,ville",
            "nom": f"ilike.%{nom}%",
            "limit": 5,
        })
        if "error" in result:
            return []
        return result.get("data", [])


supabase = SupabaseClient(service_key=os.environ.get("SUPABASE_SERVICE_KEY", ""))
