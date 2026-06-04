import httpx
from typing import Optional, Dict, Any

class ProchainsPassagesClient:
    BASE_URL = "https://prim.iledefrance-mobilites.fr/marketplace"

    def __init__(self, api_key: str):
        self.headers = {
            "apikey": api_key,
            "Accept": "application/json"
        }

    async def get_stop_monitoring(self, monitoring_ref: str, line_ref: Optional[str] = None) -> Dict[str, Any]:
        params = {"MonitoringRef": monitoring_ref}
        if line_ref:
            params["LineRef"] = line_ref
        url = f"{self.BASE_URL}/stop-monitoring"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                print(f"HTTP error occurred: {e}")
                print(f"Response details: {e.response.text}")
                return {"error": f"StopMonitoring API Error {e.response.status_code}", "details": e.response.text}
            except Exception as e:
                print(f"An error occurred: {e}")
                return {"error": "Internal client error", "details": str(e)}
