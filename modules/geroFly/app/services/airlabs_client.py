import httpx
from typing import Any

_SCHEDULE_KEYS = (
    "flight_iata", "airline_iata", "cs_airline_iata", "cs_flight_iata",
    "dep_iata", "arr_iata",
    "dep_time", "dep_estimated", "dep_actual",
    "arr_time", "arr_estimated", "arr_actual",
    "dep_terminal", "dep_gate",
    "arr_terminal", "arr_gate", "arr_baggage",
    "duration", "dep_delayed", "arr_delayed", "status",
)

_FLIGHT_KEYS = (
    "flight_iata", "airline_iata", "cs_airline_iata", "cs_flight_iata",
    "dep_iata", "arr_iata",
    "dep_time", "dep_estimated", "dep_actual",
    "arr_time", "arr_estimated", "arr_actual",
    "dep_terminal", "dep_gate",
    "arr_terminal", "arr_gate", "arr_baggage",
    "duration", "dep_delayed", "arr_delayed", "status",
    "lat", "lng", "alt", "dir", "speed", "v_speed",
    "reg_number", "aircraft_icao", "model", "manufacturer",
    "type", "engine", "engine_count", "built", "age",
    "updated",
)

_LIVE_KEYS = (
    "flight_iata", "airline_iata",
    "dep_iata", "arr_iata",
    "lat", "lng", "alt", "dir", "speed", "v_speed",
    "reg_number", "aircraft_icao",
    "status", "updated",
)

_DELAY_KEYS = (
    "flight_iata", "airline_iata",
    "dep_iata", "arr_iata",
    "dep_time", "dep_estimated",
    "arr_time", "arr_estimated",
    "dep_terminal", "dep_gate",
    "arr_terminal", "arr_gate",
    "dep_delayed", "arr_delayed", "status",
)

_AIRPORT_KEYS = (
    "iata_code", "name", "city", "country_code", "timezone",
    "lat", "lng", "alt", "runways", "departures", "connections",
    "is_major", "is_international",
)

_AIRLINE_KEYS = (
    "iata_code", "name", "country_code",
    "is_scheduled", "is_passenger", "is_cargo", "is_international",
    "total_aircrafts", "average_fleet_age",
    "accidents_last_5y", "crashes_last_5y",
)


def _pick(d: dict, keys: tuple) -> dict:
    return {k: d[k] for k in keys if k in d}


class AirlabsClient:
    """Async client for the Airlabs API v9."""

    BASE_URL = "https://airlabs.co/api/v9"

    def __init__(self, api_key: str):
        self._init_key = api_key

    def _key(self) -> str:
        return self._init_key or os.environ.get("AIRLABS_API_KEY", "")

    async def _get(self, path: str, params: dict[str, Any]) -> dict:
        key = self._key()
        if not key or key == "your_airlabs_api_key_here":
            return {"error": "API key is missing or invalid. Please configure the .env file."}
        params["api_key"] = key
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(f"{self.BASE_URL}{path}", params=params)
                response.raise_for_status()
                data = response.json()
                if "error" in data:
                    msg = data["error"].get("message", str(data["error"]))
                    return {"error": f"Airlabs API error: {msg}"}
                return data
            except httpx.HTTPStatusError as e:
                return {"error": f"Airlabs API error {e.response.status_code}", "details": e.response.text[:200]}
            except Exception as e:
                return {"error": "Internal client error", "details": str(e)}

    async def get_airport(self, iata_code: str) -> dict:
        data = await self._get("/airports", {"iata_code": iata_code})
        if "error" in data:
            return data
        results = data.get("response", [])
        if not results:
            return {"error": f"Airport '{iata_code}' not found"}
        return _pick(results[0], _AIRPORT_KEYS)

    async def get_departures(self, iata_code: str, limit: int = 20) -> dict:
        data = await self._get("/schedules", {"dep_iata": iata_code, "limit": min(limit, 50)})
        if "error" in data:
            return data
        flights = data.get("response", [])
        return {"count": len(flights), "departures": [_pick(f, _SCHEDULE_KEYS) for f in flights]}

    async def get_arrivals(self, iata_code: str, limit: int = 20) -> dict:
        data = await self._get("/schedules", {"arr_iata": iata_code, "limit": min(limit, 50)})
        if "error" in data:
            return data
        flights = data.get("response", [])
        return {"count": len(flights), "arrivals": [_pick(f, _SCHEDULE_KEYS) for f in flights]}

    async def get_live_flights(self, iata_code: str, direction: str = "departures") -> dict:
        params = {"arr_iata": iata_code} if direction == "arrivals" else {"dep_iata": iata_code}
        data = await self._get("/flights", params)
        if "error" in data:
            return data
        flights = data.get("response", [])
        trimmed = [_pick(f, _LIVE_KEYS) for f in flights[:30]]
        return {"count": len(flights), "shown": len(trimmed), "flights": trimmed}

    async def get_flight(self, flight_iata: str) -> dict:
        data = await self._get("/flight", {"flight_iata": flight_iata})
        if "error" in data:
            return data
        response = data.get("response")
        if isinstance(response, list):
            result = response[0] if response else None
        else:
            result = response
        if result is None:
            return {"error": f"Flight '{flight_iata}' not found"}
        return _pick(result, _FLIGHT_KEYS)

    async def get_delayed_flights(self, iata_code: str, direction: str = "departures", min_delay: int = 30) -> dict:
        if direction == "arrivals":
            params = {"arr_iata": iata_code, "delay": max(30, min_delay), "type": "arrivals"}
        else:
            params = {"dep_iata": iata_code, "delay": max(30, min_delay), "type": "departures"}
        data = await self._get("/delays", params)
        if "error" in data:
            return data
        flights = data.get("response", [])
        return {"count": len(flights), "delays": [_pick(f, _DELAY_KEYS) for f in flights]}

    async def get_airline(self, iata_code: str) -> dict:
        data = await self._get("/airlines", {"iata_code": iata_code})
        if "error" in data:
            return data
        results = data.get("response", [])
        if not results:
            return {"error": f"Airline '{iata_code}' not found"}
        return _pick(results[0], _AIRLINE_KEYS)
