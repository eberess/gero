import httpx
from typing import Optional, Dict, Any

class IDFMClient:
    """
    Client pour interagir avec l'API Navitia V2 de PRIM (Île-de-France Mobilités)
    """
    BASE_URL = "https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "apikey": self.api_key,
            "Accept": "application/json"
        }

    async def get_departures(self, stop_area_id: str) -> Dict[str, Any]:
        """
        Récupère les prochains départs pour une zone d'arrêt donnée.
        """
        url = f"{self.BASE_URL}/stop_areas/{stop_area_id}/departures"
        return await self._make_request(url)

    async def get_journey(self, from_query: str, to_query: str) -> Dict[str, Any]:
        """
        Calcule un itinéraire entre deux points/arrêts.
        from_query et to_query peuvent être des coordonnées (lon;lat) ou des IDs.
        """
        url = f"{self.BASE_URL}/journeys"
        params = {
            "from": from_query,
            "to": to_query
        }
        return await self._make_request(url, params=params)

    async def search_place(self, query: str) -> Dict[str, Any]:
        """
        Recherche un lieu ou un arrêt par son nom.
        Utile pour trouver les IDs à passer à get_journey ou get_departures.
        """
        url = f"{self.BASE_URL}/places"
        params = {"q": query}
        return await self._make_request(url, params=params)

    async def _make_request(self, url: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        if not self.api_key or self.api_key == "your_idfm_api_key_here":
            return {"error": "API Key is missing or invalid. Please configure the .env file."}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                print(f"HTTP error occurred: {e}")
                print(f"Response details: {e.response.text}")
                return {"error": f"IDFM API Error {e.response.status_code}", "details": e.response.text}
            except Exception as e:
                print(f"An error occurred: {e}")
                return {"error": "Internal client error", "details": str(e)}
