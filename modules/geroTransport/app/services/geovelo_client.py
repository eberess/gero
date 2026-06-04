import httpx
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class Waypoint(BaseModel):
    latitude: float
    longitude: float
    title: Optional[str] = None

class BikeDetails(BaseModel):
    profile: str = "MEDIAN"
    bikeType: str = "TRADITIONAL"
    averageSpeed: Optional[int] = None
    eBike: bool = False

class GeoveloBikeRequest(BaseModel):
    start: Waypoint
    end: Waypoint
    profile: str = "MEDIAN"
    bike_type: str = "TRADITIONAL"
    ebike: bool = False
    instructions: bool = False
    elevations: bool = False
    geometry: bool = False

class GeoveloClient:
    BASE_URL = "https://prim.iledefrance-mobilites.fr/marketplace"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "apikey": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    async def compute_route(self, request: GeoveloBikeRequest) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/computedroutes"
        params = {
            "instructions": str(request.instructions).lower(),
            "elevations": str(request.elevations).lower(),
            "geometry": str(request.geometry).lower(),
        }
        body = {
            "waypoints": [
                {
                    "latitude": request.start.latitude,
                    "longitude": request.start.longitude,
                    "title": request.start.title,
                },
                {
                    "latitude": request.end.latitude,
                    "longitude": request.end.longitude,
                    "title": request.end.title,
                },
            ],
            "bikeDetails": {
                "profile": request.profile,
                "bikeType": request.bike_type,
                "eBike": request.ebike,
            }
        }
        return await self._make_request(url, params=params, body=body)

    async def _make_request(self, url: str, params: Optional[Dict[str, str]] = None, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.api_key or self.api_key == "your_idfm_api_key_here":
            return {"error": "API Key is missing or invalid. Please configure the .env file."}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=self.headers, params=params, json=body)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                print(f"HTTP error occurred: {e}")
                print(f"Response details: {e.response.text}")
                return {"error": f"Geovelo API Error {e.response.status_code}", "details": e.response.text}
            except Exception as e:
                print(f"An error occurred: {e}")
                return {"error": "Internal client error", "details": str(e)}
