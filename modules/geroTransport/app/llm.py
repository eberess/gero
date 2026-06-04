from fastapi import APIRouter, Query, HTTPException
from app.dependencies import idfm_client, geovelo_client, velib_client, infotrafic_client, prochainspassages_client
from app.services.geovelo_client import GeoveloBikeRequest, Waypoint
from datetime import datetime

router = APIRouter(prefix="/llm", tags=["llm"])

def extract_stif_code(ref: str) -> str:
    if ref.startswith("STIF:Line::"):
        return ref.split(":")[3]
    return ref

def build_line_map(place_data: dict) -> dict:
    places = place_data.get("places", [])
    if not places:
        return {}
    p = places[0]
    obj = p.get(p.get("embedded_type", ""), {})
    lines = obj.get("lines", [])
    mapping = {}
    for line in lines:
        lid = line.get("id", "")
        code = lid.split(":")[-1] if ":" in lid else lid
        mode = line.get("commercial_mode", {}).get("name", "Bus")
        mapping[code] = {
            "name": line.get("code", line.get("name", code)),
            "mode": mode,
        }
    return mapping

from zoneinfo import ZoneInfo

PARIS_TZ = ZoneInfo("Europe/Paris")

def format_time(iso: str) -> str:
    if not iso:
        return "?"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        dt_local = dt.astimezone(PARIS_TZ)
        return dt_local.strftime("%H:%M")
    except (ValueError, AttributeError):
        return iso

def to_stif_monitoring_ref(navitia_id: str) -> str:
    if navitia_id.startswith("STIF:"):
        return navitia_id
    if navitia_id.startswith("stop_area:IDFM:"):
        num = navitia_id.split(":")[-1]
        return f"STIF:StopArea:SP:{num}:"
    if navitia_id.startswith("stop_point:IDFM:"):
        num = navitia_id.split(":")[-1]
        return f"STIF:StopPoint:Q:{num}:"
    return navitia_id

def extract_coords(place_data: dict) -> tuple:
    places = place_data.get("places", [])
    if not places:
        raise HTTPException(status_code=404, detail="Lieu introuvable")
    p = places[0]
    embedded_type = p.get("embedded_type")
    obj = p.get(embedded_type)
    if not obj or "coord" not in obj:
        raise HTTPException(status_code=404, detail="Coordonnées introuvables pour ce lieu")
    coord = obj["coord"]
    return float(coord["lat"]), float(coord["lon"])

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    from math import radians, sin, cos, sqrt, asin
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * asin(sqrt(a))


@router.get("/next")
async def llm_next(stop: str = Query(..., description="Nom de l'arrêt (ex: Nation)")):
    if not stop.startswith("STIF:"):
        place_data = await idfm_client.search_place(stop)
        places = place_data.get("places", [])
        if not places:
            raise HTTPException(status_code=404, detail="Arrêt introuvable")
        monitoring_ref = to_stif_monitoring_ref(places[0]["id"])
        line_map = build_line_map(place_data)
    else:
        monitoring_ref = stop
        line_map = {}

    raw = await prochainspassages_client.get_stop_monitoring(monitoring_ref)
    deliveries = raw.get("Siri", {}).get("ServiceDelivery", {}).get("StopMonitoringDelivery", [])
    visits = deliveries[0].get("MonitoredStopVisit", []) if deliveries else []

    departures = []
    seen = {}
    for v in visits:
        j = v.get("MonitoredVehicleJourney", {})
        line_ref = j.get("LineRef", {}).get("value", "")
        dest = j.get("DestinationName", [{}])[0].get("value", "?")
        call = j.get("MonitoredCall", {})
        expected = call.get("ExpectedArrivalTime") or call.get("ExpectedDepartureTime") or ""
        code = extract_stif_code(line_ref)
        info = line_map.get(code, {})
        line_name = info.get("name", code)
        mode = info.get("mode", "")
        key = f"{code}|{dest}"
        if key not in seen:
            seen[key] = {"line": line_name, "mode": mode, "direction": dest, "times": []}
        seen[key]["times"].append(format_time(expected))

    for v in seen.values():
        v["next"] = v["times"][0]
        v["following"] = v["times"][1:4]
        departures.append(v)

    departures.sort(key=lambda x: x["next"])
    return {"data": {"stop": stop, "departures": departures[:10]}}


@router.get("/journey")
async def llm_journey(
    from_name: str = Query(..., description="Lieu de départ (ex: Nation)"),
    to_name: str = Query(..., description="Lieu d'arrivée (ex: Anvers)")
):
    from_data = await idfm_client.search_place(from_name)
    to_data = await idfm_client.search_place(to_name)
    from_places = from_data.get("places", [])
    to_places = to_data.get("places", [])
    if not from_places or not to_places:
        raise HTTPException(status_code=404, detail="Lieu introuvable")

    raw = await idfm_client.get_journey(from_places[0]["id"], to_places[0]["id"])
    journeys = raw.get("journeys", [])
    if not journeys:
        return {"data": {"error": "Aucun itinéraire trouvé"}}

    j = journeys[0]
    steps = []
    for s in j.get("sections", []):
        infos = s.get("display_informations", {})
        mode = s.get("mode") or (infos.get("commercial_mode", "").lower() if infos else None) or s.get("type", "walking")
        if mode == "crow_fly":
            mode = "walking"
        step = {
            "mode": mode,
            "from": s.get("from", {}).get("name", ""),
            "to": s.get("to", {}).get("name", ""),
            "departure": format_time(s.get("departure_date_time", "")),
            "arrival": format_time(s.get("arrival_date_time", "")),
            "duration_min": round(s.get("duration", 0) / 60),
        }
        if mode == "walking":
            props = s.get("geojson", {}).get("properties", [])
            if props and isinstance(props, list) and props[0].get("length"):
                step["distance_m"] = round(props[0]["length"])
        if infos:
            step["line"] = infos.get("code", "")
            step["direction"] = infos.get("direction", "")
        steps.append(step)

    return {
        "data": {
            "departure": format_time(j.get("departure_date_time", "")),
            "arrival": format_time(j.get("arrival_date_time", "")),
            "duration_min": round(j.get("duration", 0) / 60),
            "nb_transfers": j.get("nb_transfers", 0),
            "steps": steps,
        }
    }


@router.get("/traffic")
async def llm_traffic():
    raw = await infotrafic_client.get_disruptions()
    disruptions = raw.get("disruptions", [])
    major = []
    for d in disruptions:
        severity = d.get("severity", "")
        if severity in ("BLOQUANTE", "IMPORTANTE"):
            major.append({
                "title": d.get("title", ""),
                "message": d.get("shortMessage", d.get("message", "")),
                "severity": severity,
                "cause": d.get("cause", ""),
            })
    return {"data": major[:10]}


@router.get("/velib/nearby")
async def llm_velib_nearby(
    name: str = Query(..., description="Nom du lieu (ex: Nation)"),
    limit: int = 3
):
    place_data = await idfm_client.search_place(name)
    lat, lon = extract_coords(place_data)

    info_data = await velib_client.get_station_information()
    status_data = await velib_client.get_station_status()

    stations_info = info_data.get("data", {}).get("stations", [])
    stations_status = status_data.get("data", {}).get("stations", [])
    status_map = {s["station_id"]: s for s in stations_status}

    ranked = []
    for s in stations_info:
        dist = haversine(lat, lon, s["lat"], s["lon"])
        avail = status_map.get(s["station_id"], {})
        ranked.append({
            "name": s.get("name"),
            "distance_km": round(dist, 3),
            "total_bikes": avail.get("num_bikes_available", 0),
            "mechanical": (avail.get("num_bikes_available_types") or [{}])[0].get("mechanical", 0),
            "electrical": (avail.get("num_bikes_available_types") or [{}])[1].get("ebike", 0) if avail.get("num_bikes_available_types") and len(avail.get("num_bikes_available_types", [])) > 1 else 0,
            "free_docks": avail.get("num_docks_available", 0),
        })

    ranked.sort(key=lambda x: x["distance_km"])
    return {"data": ranked[:limit]}
