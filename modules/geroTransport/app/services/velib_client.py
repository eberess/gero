import httpx
from typing import Optional, Dict, Any

class VelibClient:
    BASE_URL = "https://prim.iledefrance-mobilites.fr/marketplace/velib"

    def __init__(self, api_key: str = ""):
        self.headers = {
            "apikey": api_key,
            "Accept": "application/json"
        }

    async def get_station_status(self) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/station_status.json"
        return await self._make_request(url)

    async def get_station_information(self) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/station_information.json"
        return await self._make_request(url)

    async def get_system_information(self) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/system_information.json"
        return await self._make_request(url)

    async def _make_request(self, url: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                print(f"HTTP error occurred: {e}")
                print(f"Response details: {e.response.text}")
                return {"error": f"Velib API Error {e.response.status_code}", "details": e.response.text}
            except Exception as e:
                print(f"An error occurred: {e}")
                return {"error": "Internal client error", "details": str(e)}
