from fastapi import APIRouter, Query
from pydantic import BaseModel
from app.dependencies import googlemaps_client, ROBOT_LAT, ROBOT_LNG

router = APIRouter(prefix="/llm", tags=["llm"])


class RouteMatrixRequest(BaseModel):
    origins: list[dict]
    destinations: list[dict]
    travel_mode: str = "WALK"


@router.get("/nearby")
async def llm_nearby(
    lat: float = Query(ROBOT_LAT),
    lng: float = Query(ROBOT_LNG),
    radius_m: float = Query(500.0),
    types: str = Query(None, description="Comma-separated place types, e.g. restaurant,atm"),
    limit: int = Query(10, ge=1, le=20),
):
    place_types = [t.strip() for t in types.split(",")] if types else None
    data = await googlemaps_client.search_nearby(lat, lng, radius_m, place_types, limit)
    if "error" in data:
        return {"error": data["error"]}
    places = [
        {
            "name": p.get("displayName", {}).get("text"),
            "address": p.get("formattedAddress"),
            "place_id": p.get("id"),
            "types": p.get("types", [])[:3],
            "open_now": p.get("currentOpeningHours", {}).get("openNow"),
            "rating": p.get("rating"),
            "lat": p.get("location", {}).get("latitude"),
            "lng": p.get("location", {}).get("longitude"),
        }
        for p in data.get("places", [])
    ]
    return {"count": len(places), "places": places}


@router.get("/find")
async def llm_find(
    query: str = Query(...),
    lat: float = Query(ROBOT_LAT),
    lng: float = Query(ROBOT_LNG),
):
    data = await googlemaps_client.search_text(query, lat, lng)
    if "error" in data:
        return {"error": data["error"]}
    places = [
        {
            "name": p.get("displayName", {}).get("text"),
            "address": p.get("formattedAddress"),
            "place_id": p.get("id"),
            "open_now": p.get("currentOpeningHours", {}).get("openNow"),
            "rating": p.get("rating"),
            "website": p.get("websiteUri"),
        }
        for p in data.get("places", [])
    ]
    return {"query": query, "count": len(places), "places": places}


@router.get("/place")
async def llm_place(place_id: str = Query(...)):
    data = await googlemaps_client.get_place_details(place_id)
    if "error" in data:
        return {"error": data["error"]}
    hours = []
    for period in (data.get("regularOpeningHours") or {}).get("periods", []):
        open_info = period.get("open", {})
        close_info = period.get("close", {})
        hours.append({
            "day": open_info.get("day"),
            "open": f"{open_info.get('hour', 0):02d}:{open_info.get('minute', 0):02d}",
            "close": f"{close_info.get('hour', 0):02d}:{close_info.get('minute', 0):02d}" if close_info else None,
        })
    accessibility = data.get("accessibilityOptions") or {}
    return {
        "name": data.get("displayName", {}).get("text"),
        "address": data.get("formattedAddress"),
        "phone": data.get("internationalPhoneNumber"),
        "website": data.get("websiteUri"),
        "open_now": (data.get("currentOpeningHours") or {}).get("openNow"),
        "hours": hours,
        "wheelchair": accessibility.get("wheelchairAccessibleEntrance"),
        "rating": data.get("rating"),
        "rating_count": data.get("userRatingCount"),
    }


@router.get("/geocode")
async def llm_geocode(address: str = Query(...)):
    data = await googlemaps_client.geocode(address)
    if "error" in data:
        return {"error": data["error"]}
    loc = data.get("location", {})
    return {
        "address": data.get("formatted_address"),
        "lat": loc.get("lat"),
        "lng": loc.get("lng"),
        "place_id": data.get("place_id"),
    }


@router.get("/where-am-i")
async def llm_where_am_i(
    lat: float = Query(ROBOT_LAT),
    lng: float = Query(ROBOT_LNG),
):
    data = await googlemaps_client.reverse_geocode(lat, lng)
    if "error" in data:
        return {"error": data["error"]}
    return {
        "address": data.get("formatted_address"),
        "place_id": data.get("place_id"),
        "lat": lat,
        "lng": lng,
    }


@router.get("/route")
async def llm_route(
    origin_lat: float = Query(ROBOT_LAT),
    origin_lng: float = Query(ROBOT_LNG),
    dest_lat: float = Query(...),
    dest_lng: float = Query(...),
    mode: str = Query("WALK"),
):
    data = await googlemaps_client.compute_route(origin_lat, origin_lng, dest_lat, dest_lng, mode)
    if "error" in data:
        return {"error": data["error"]}
    steps = []
    for leg in data.get("legs", []):
        for step in leg.get("steps", []):
            nav = step.get("navigationInstruction", {})
            steps.append({
                "instruction": nav.get("instructions"),
                "distance_m": step.get("distanceMeters"),
            })
    return {
        "distance_m": data.get("distance_meters"),
        "duration": data.get("duration"),
        "steps": steps,
    }


@router.post("/route-matrix")
async def llm_route_matrix(request: RouteMatrixRequest):
    data = await googlemaps_client.compute_route_matrix(
        request.origins, request.destinations, request.travel_mode
    )
    if "error" in data:
        return {"error": data["error"]}
    matrix = [
        {
            "origin_index": e["origin_index"],
            "destination_index": e["destination_index"],
            "destination_address": e.get("destination_address"),
            "distance_m": (e.get("distance") or {}).get("value"),
            "duration_s": (e.get("duration") or {}).get("value"),
            "status": e.get("status"),
        }
        for e in data.get("matrix", [])
    ]
    return {"count": len(matrix), "matrix": matrix}
