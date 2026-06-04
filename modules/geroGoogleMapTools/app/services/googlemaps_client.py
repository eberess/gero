import httpx
from typing import Any

_PLACES_BASE = "https://places.googleapis.com/v1"
_GEOCODING_BASE = "https://maps.googleapis.com/maps/api/geocode/json"
_ROUTES_BASE = "https://routes.googleapis.com/directions/v2"
_DISTANCEMATRIX_BASE = "https://maps.googleapis.com/maps/api/distancematrix/json"

_MODE_MAP = {"WALK": "walking", "DRIVE": "driving", "TRANSIT": "transit", "BICYCLE": "bicycling"}


class GoogleMapsClient:
    """Async client for the Google Maps Platform APIs."""

    def __init__(self, api_key: str):
        self._init_key = api_key

    def _key(self) -> str:
        return self._init_key or os.environ.get("GOOGLE_MAPS_API_KEY", "")

    def _invalid_key(self) -> bool:
        k = self._key()
        return not k or k == "your_google_maps_api_key_here"

    async def _get(self, url: str, params: dict[str, Any]) -> dict:
        if self._invalid_key():
            return {"error": "API key is missing or invalid. Please configure the .env file."}
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                if "error_message" in data:
                    return {"error": data["error_message"]}
                return data
            except httpx.HTTPStatusError as e:
                return {"error": f"Google API error {e.response.status_code}", "details": e.response.text[:200]}
            except Exception as e:
                return {"error": "Internal client error", "details": str(e)}

    async def _post(self, url: str, payload: dict, field_mask: str) -> dict:
        if self._invalid_key():
            return {"error": "API key is missing or invalid. Please configure the .env file."}
        headers = {
            "X-Goog-Api-Key": self._key(),
            "X-Goog-FieldMask": field_mask,
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                return {"error": f"Google API error {e.response.status_code}", "details": e.response.text[:200]}
            except Exception as e:
                return {"error": "Internal client error", "details": str(e)}

    async def search_nearby(
        self,
        lat: float,
        lng: float,
        radius_m: float = 500.0,
        place_types: list[str] | None = None,
        max_results: int = 10,
    ) -> dict:
        payload: dict = {
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": lat, "longitude": lng},
                    "radius": min(radius_m, 50000.0),
                }
            },
            "maxResultCount": min(max(1, max_results), 20),
            "rankPreference": "DISTANCE",
        }
        if place_types:
            payload["includedTypes"] = place_types
        field_mask = "places.id,places.displayName,places.types,places.formattedAddress,places.location,places.rating,places.currentOpeningHours.openNow"
        data = await self._post(f"{_PLACES_BASE}/places:searchNearby", payload, field_mask)
        if "error" in data:
            return data
        return {"places": data.get("places", [])}

    async def search_text(
        self,
        query: str,
        lat: float,
        lng: float,
        radius_m: float = 2000.0,
    ) -> dict:
        payload: dict = {
            "textQuery": query,
            "maxResultCount": 10,
            "locationBias": {
                "circle": {
                    "center": {"latitude": lat, "longitude": lng},
                    "radius": min(radius_m, 50000.0),
                }
            },
        }
        field_mask = "places.id,places.displayName,places.types,places.formattedAddress,places.location,places.rating,places.currentOpeningHours.openNow,places.websiteUri"
        data = await self._post(f"{_PLACES_BASE}/places:searchText", payload, field_mask)
        if "error" in data:
            return data
        return {"places": data.get("places", [])}

    async def get_place_details(self, place_id: str) -> dict:
        if self._invalid_key():
            return {"error": "API key is missing or invalid. Please configure the .env file."}
        field_mask = (
            "id,displayName,formattedAddress,location,types,"
            "regularOpeningHours,currentOpeningHours,websiteUri,"
            "internationalPhoneNumber,accessibilityOptions,"
            "rating,userRatingCount"
        )
        headers = {
            "X-Goog-Api-Key": self._key(),
            "X-Goog-FieldMask": field_mask,
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(f"{_PLACES_BASE}/places/{place_id}", headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                return {"error": f"Google API error {e.response.status_code}", "details": e.response.text[:200]}
            except Exception as e:
                return {"error": "Internal client error", "details": str(e)}

    async def geocode(self, address: str) -> dict:
        data = await self._get(_GEOCODING_BASE, {"address": address, "key": self._key()})
        if "error" in data:
            return data
        results = data.get("results", [])
        if not results:
            return {"error": f"No geocoding results for: {address}"}
        top = results[0]
        return {
            "formatted_address": top.get("formatted_address"),
            "location": top["geometry"]["location"],
            "place_id": top.get("place_id"),
            "types": top.get("types", []),
        }

    async def reverse_geocode(self, lat: float, lng: float) -> dict:
        data = await self._get(_GEOCODING_BASE, {"latlng": f"{lat},{lng}", "key": self._key()})
        if "error" in data:
            return data
        results = data.get("results", [])
        if not results:
            return {"error": f"No results for coordinates ({lat}, {lng})"}
        top = results[0]
        return {
            "formatted_address": top.get("formatted_address"),
            "place_id": top.get("place_id"),
            "types": top.get("types", []),
            "address_components": top.get("address_components", []),
        }

    async def compute_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        travel_mode: str = "WALK",
    ) -> dict:
        payload = {
            "origin": {"location": {"latLng": {"latitude": origin_lat, "longitude": origin_lng}}},
            "destination": {"location": {"latLng": {"latitude": dest_lat, "longitude": dest_lng}}},
            "travelMode": travel_mode.upper(),
            "computeAlternativeRoutes": False,
        }
        field_mask = "routes.distanceMeters,routes.duration,routes.legs.steps.navigationInstruction,routes.legs.distanceMeters,routes.legs.duration"
        data = await self._post(f"{_ROUTES_BASE}:computeRoutes", payload, field_mask)
        if "error" in data:
            return data
        routes = data.get("routes", [])
        if not routes:
            return {"error": "No route found between the given points"}
        route = routes[0]
        return {
            "distance_meters": route.get("distanceMeters"),
            "duration": route.get("duration"),
            "legs": route.get("legs", []),
        }

    async def compute_route_matrix(
        self,
        origins: list[dict],
        destinations: list[dict],
        travel_mode: str = "WALK",
    ) -> dict:
        mode = _MODE_MAP.get(travel_mode.upper(), "walking")
        origins_str = "|".join(f"{o['lat']},{o['lng']}" for o in origins)
        destinations_str = "|".join(f"{d['lat']},{d['lng']}" for d in destinations)
        data = await self._get(
            _DISTANCEMATRIX_BASE,
            {"origins": origins_str, "destinations": destinations_str, "mode": mode, "key": self._key()},
        )
        if "error" in data:
            return data
        rows = data.get("rows", [])
        dest_addresses = data.get("destination_addresses", [])
        matrix = []
        for o_idx, row in enumerate(rows):
            for d_idx, element in enumerate(row.get("elements", [])):
                matrix.append({
                    "origin_index": o_idx,
                    "destination_index": d_idx,
                    "destination_address": dest_addresses[d_idx] if d_idx < len(dest_addresses) else None,
                    "distance": element.get("distance"),
                    "duration": element.get("duration"),
                    "status": element.get("status"),
                })
        return {"matrix": matrix}
