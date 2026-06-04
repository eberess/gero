import httpx
from typing import Dict, Any

class InfoTraficClient:
    BASE_URL = "https://prim.iledefrance-mobilites.fr/marketplace/disruptions_bulk"

    def __init__(self, api_key: str):
        self.headers = {
            "apikey": api_key,
            "Accept": "application/json"
        }

    async def get_disruptions(self) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/disruptions/v2"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                print(f"HTTP error occurred: {e}")
                print(f"Response details: {e.response.text}")
                return {"error": f"InfoTrafic API Error {e.response.status_code}", "details": e.response.text}
            except Exception as e:
                print(f"An error occurred: {e}")
                return {"error": "Internal client error", "details": str(e)}
