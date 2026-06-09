from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.dependencies import idfm_client, geovelo_client, velib_client, infotrafic_client, prochainspassages_client
from app.services.geovelo_client import GeoveloClient, GeoveloBikeRequest, Waypoint
from app.llm import router as llm_router
from pydantic import BaseModel

app = FastAPI(
    title="geroTransport API",
    description="Module d'intelligence de transport pour Unitree G1",
    version="2.0.0"
)

GENERIC_ERRORS = {
    400: "Requête invalide",
    401: "Non authentifié",
    403: "Accès refusé",
    404: "Ressource non trouvée",
    422: "Données invalides",
    500: "Erreur interne du serveur",
}


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": GENERIC_ERRORS.get(exc.status_code, "Erreur")},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": GENERIC_ERRORS[500]})


app.include_router(llm_router)

class BikeSearchRequest(BaseModel):
    from_name: str
    to_name: str
    profile: str = "MEDIAN"
    bike_type: str = "TRADITIONAL"
    ebike: bool = False

class VelibNearbyRequest(BaseModel):
    name: str | None = None
    lat: float | None = None
    lon: float | None = None
    limit: int = 5

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

@app.get("/")
def read_root():
    return {"status": "ok", "service": "geroTransport"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/transport/search")
async def search_place(q: str = Query(..., description="Nom de l'arrêt ou lieu")):
    data = await idfm_client.search_place(q)
    return {"data": data}

@app.get("/transport/cdg/departures")
async def get_cdg_departures(stop_id: str = Query("stop_area:IDFM:71876", description="ID de l'arrêt")):
    data = await idfm_client.get_departures(stop_id)
    return {"data": data}

@app.get("/transport/journey")
async def get_journey(
    from_point: str = Query(..., description="Départ (ID Navitia ou lon;lat)"),
    to_point: str = Query(..., description="Arrivée (ID Navitia ou lon;lat)")
):
    data = await idfm_client.get_journey(from_point, to_point)
    return {"data": data}

@app.get("/transport/velib/stations")
async def get_velib_stations():
    data = await velib_client.get_station_information()
    return {"data": data}

@app.get("/transport/velib/status")
async def get_velib_status():
    data = await velib_client.get_station_status()
    return {"data": data}

@app.post("/transport/velib/nearby")
async def get_nearest_velib(request: VelibNearbyRequest):
    if request.lat is not None and request.lon is not None:
        lat, lon = request.lat, request.lon
    elif request.name:
        place_data = await idfm_client.search_place(request.name)
        lat, lon = extract_coords(place_data)
    else:
        raise HTTPException(status_code=400, detail="Fournissez un nom de lieu ou des coordonnées")

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
            "station_id": s["station_id"],
            "name": s.get("name"),
            "lat": s.get("lat"),
            "lon": s.get("lon"),
            "capacity": s.get("capacity"),
            "distance_km": round(dist, 3),
            "bikes_available": avail.get("num_bikes_available", "?"),
            "docks_available": avail.get("num_docks_available", "?"),
            "mechanical_bikes": (avail.get("num_bikes_available_types") or [{}])[0].get("mechanical", 0) if avail.get("num_bikes_available_types") else None,
            "electrical_bikes": (avail.get("num_bikes_available_types") or [{}])[1].get("ebike", 0) if avail.get("num_bikes_available_types") and len(avail.get("num_bikes_available_types", [])) > 1 else None,
        })

    ranked.sort(key=lambda x: x["distance_km"])
    return {"data": ranked[:request.limit]}

@app.get("/transport/traffic")
async def get_traffic_info():
    data = await infotrafic_client.get_disruptions()
    return {"data": data}

@app.get("/transport/next")
async def get_next_departures(
    stop: str = Query(..., description="Nom de l'arrêt ou ID STIF"),
    line: str = Query(None, description="Filtrer par ligne (ex: STIF:Line::C01742:)")
):
    if not stop.startswith("STIF:"):
        place_data = await idfm_client.search_place(stop)
        places = place_data.get("places", [])
        if not places:
            raise HTTPException(status_code=404, detail="Arrêt introuvable")
        monitoring_ref = to_stif_monitoring_ref(places[0]["id"])
    else:
        monitoring_ref = stop
    data = await prochainspassages_client.get_stop_monitoring(monitoring_ref, line)
    return {"data": data}

@app.post("/transport/bike")
async def get_bike_route(request: GeoveloBikeRequest):
    data = await geovelo_client.compute_route(request)
    return {"data": data}

@app.post("/transport/bike/search")
async def get_bike_route_by_name(request: BikeSearchRequest):
    from_data = await idfm_client.search_place(request.from_name)
    to_data = await idfm_client.search_place(request.to_name)
    from_lat, from_lon = extract_coords(from_data)
    to_lat, to_lon = extract_coords(to_data)

    bike_request = GeoveloBikeRequest(
        start=Waypoint(latitude=from_lat, longitude=from_lon, title=request.from_name),
        end=Waypoint(latitude=to_lat, longitude=to_lon, title=request.to_name),
        profile=request.profile,
        bike_type=request.bike_type,
        ebike=request.ebike,
    )
    data = await geovelo_client.compute_route(bike_request)
    return {"data": data}
