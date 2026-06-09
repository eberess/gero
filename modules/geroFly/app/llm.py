from fastapi import APIRouter, Query, HTTPException
from app.dependencies import airlabs_client

router = APIRouter(prefix="/llm", tags=["llm"])


def _time(s: str | None) -> str | None:
    """Extract HH:MM from Airlabs datetime string 'YYYY-MM-DD HH:MM:SS'."""
    if not s:
        return None
    parts = s.split(" ")
    if len(parts) == 2:
        return parts[1][:5]
    return s


@router.get("/airport")
async def llm_airport(iata: str = Query("CDG")):
    data = await airlabs_client.get_airport(iata.upper())
    if "error" in data:
        raise HTTPException(status_code=502, detail="Erreur de l'API vols")
    return {
        "iata": data.get("iata_code"),
        "name": data.get("name"),
        "city": data.get("city"),
        "country": data.get("country_code"),
        "timezone": data.get("timezone"),
        "runways": data.get("runways"),
        "is_major": data.get("is_major"),
        "is_international": data.get("is_international"),
    }


@router.get("/departures")
async def llm_departures(iata: str = Query("CDG"), limit: int = Query(10, ge=1, le=50)):
    data = await airlabs_client.get_departures(iata.upper(), limit)
    if "error" in data:
        raise HTTPException(status_code=502, detail="Erreur de l'API vols")
    flights = [
        {
            "flight": f.get("flight_iata"),
            "airline": f.get("airline_iata"),
            "destination": f.get("arr_iata"),
            "scheduled": _time(f.get("dep_time")),
            "estimated": _time(f.get("dep_estimated")),
            "terminal": f.get("dep_terminal"),
            "gate": f.get("dep_gate"),
            "status": f.get("status"),
            "delay_min": f.get("dep_delayed"),
        }
        for f in data.get("departures", [])
    ]
    return {"airport": iata.upper(), "count": len(flights), "departures": flights}


@router.get("/arrivals")
async def llm_arrivals(iata: str = Query("CDG"), limit: int = Query(10, ge=1, le=50)):
    data = await airlabs_client.get_arrivals(iata.upper(), limit)
    if "error" in data:
        raise HTTPException(status_code=502, detail="Erreur de l'API vols")
    flights = [
        {
            "flight": f.get("flight_iata"),
            "airline": f.get("airline_iata"),
            "origin": f.get("dep_iata"),
            "scheduled": _time(f.get("arr_time")),
            "estimated": _time(f.get("arr_estimated")),
            "terminal": f.get("arr_terminal"),
            "gate": f.get("arr_gate"),
            "status": f.get("status"),
            "delay_min": f.get("arr_delayed"),
        }
        for f in data.get("arrivals", [])
    ]
    return {"airport": iata.upper(), "count": len(flights), "arrivals": flights}


@router.get("/live")
async def llm_live(
    iata: str = Query("CDG"),
    direction: str = Query("departures", pattern="^(departures|arrivals)$"),
):
    data = await airlabs_client.get_live_flights(iata.upper(), direction)
    if "error" in data:
        raise HTTPException(status_code=502, detail="Erreur de l'API vols")
    flights = [
        {
            "flight": f.get("flight_iata"),
            "airline": f.get("airline_iata"),
            "from": f.get("dep_iata"),
            "to": f.get("arr_iata"),
            "lat": f.get("lat"),
            "lng": f.get("lng"),
            "alt": f.get("alt"),
            "speed": f.get("speed"),
            "status": f.get("status"),
        }
        for f in data.get("flights", [])
    ]
    return {"airport": iata.upper(), "direction": direction, "count": len(flights), "flights": flights}


@router.get("/flight")
async def llm_flight(flight_iata: str = Query(...)):
    data = await airlabs_client.get_flight(flight_iata.upper())
    if "error" in data:
        raise HTTPException(status_code=502, detail="Erreur de l'API vols")
    position = None
    if data.get("lat") is not None:
        position = {"lat": data["lat"], "lng": data["lng"], "alt": data.get("alt"), "speed": data.get("speed")}
    return {
        "flight": data.get("flight_iata"),
        "airline": data.get("airline_iata"),
        "from": data.get("dep_iata"),
        "to": data.get("arr_iata"),
        "scheduled_dep": _time(data.get("dep_time")),
        "estimated_dep": _time(data.get("dep_estimated")),
        "actual_dep": _time(data.get("dep_actual")),
        "scheduled_arr": _time(data.get("arr_time")),
        "estimated_arr": _time(data.get("arr_estimated")),
        "actual_arr": _time(data.get("arr_actual")),
        "dep_terminal": data.get("dep_terminal"),
        "dep_gate": data.get("dep_gate"),
        "arr_terminal": data.get("arr_terminal"),
        "arr_gate": data.get("arr_gate"),
        "status": data.get("status"),
        "delay_dep": data.get("dep_delayed"),
        "delay_arr": data.get("arr_delayed"),
        "aircraft": data.get("model"),
        "position": position,
    }


@router.get("/delays")
async def llm_delays(
    iata: str = Query("CDG"),
    direction: str = Query("departures", pattern="^(departures|arrivals)$"),
    min_delay: int = Query(30, ge=30),
):
    data = await airlabs_client.get_delayed_flights(iata.upper(), direction, min_delay)
    if "error" in data:
        raise HTTPException(status_code=502, detail="Erreur de l'API vols")
    delays = [
        {
            "flight": f.get("flight_iata"),
            "airline": f.get("airline_iata"),
            "from": f.get("dep_iata"),
            "to": f.get("arr_iata"),
            "scheduled": _time(f.get("dep_time") if direction == "departures" else f.get("arr_time")),
            "estimated": _time(f.get("dep_estimated") if direction == "departures" else f.get("arr_estimated")),
            "delay_min": f.get("dep_delayed") if direction == "departures" else f.get("arr_delayed"),
            "terminal": f.get("dep_terminal") if direction == "departures" else f.get("arr_terminal"),
            "gate": f.get("dep_gate") if direction == "departures" else f.get("arr_gate"),
        }
        for f in data.get("delays", [])
    ]
    return {"airport": iata.upper(), "direction": direction, "count": len(delays), "delays": delays}


@router.get("/airline")
async def llm_airline(iata: str = Query(...)):
    data = await airlabs_client.get_airline(iata.upper())
    if "error" in data:
        raise HTTPException(status_code=502, detail="Erreur de l'API vols")
    return {
        "iata": data.get("iata_code"),
        "name": data.get("name"),
        "country": data.get("country_code"),
        "fleet_size": data.get("total_aircrafts"),
        "avg_fleet_age": data.get("average_fleet_age"),
        "is_passenger": data.get("is_passenger"),
        "is_cargo": data.get("is_cargo"),
        "accidents_5y": data.get("accidents_last_5y"),
    }
