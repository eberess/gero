from fastapi import FastAPI, Query
from pydantic import BaseModel
from app.dependencies import googlemaps_client, ROBOT_LAT, ROBOT_LNG
from app.llm import router as llm_router

app = FastAPI(
    title="geroGoogleMapTools API",
    description="Maps and navigation microservice for GERO — Google Maps Platform",
    version="1.0.0",
)

app.include_router(llm_router)


class LatLng(BaseModel):
    lat: float
    lng: float


class NearbySearchRequest(BaseModel):
    lat: float = ROBOT_LAT
    lng: float = ROBOT_LNG
    radius_m: float = 500.0
    place_types: list[str] | None = None
    max_results: int = 10


class RouteMatrixRequest(BaseModel):
    origins: list[LatLng]
    destinations: list[LatLng]
    travel_mode: str = "WALK"


@app.get("/")
def read_root():
    return {"status": "ok", "service": "geroGoogleMapTools"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/maps/places/nearby")
async def search_nearby_places(request: NearbySearchRequest):
    data = await googlemaps_client.search_nearby(
        request.lat, request.lng, request.radius_m, request.place_types, request.max_results
    )
    return {"data": data}


@app.get("/maps/places/text")
async def search_places_text(
    query: str = Query(...),
    lat: float = Query(ROBOT_LAT),
    lng: float = Query(ROBOT_LNG),
    radius_m: float = Query(2000.0),
):
    data = await googlemaps_client.search_text(query, lat, lng, radius_m)
    return {"data": data}


@app.get("/maps/places/{place_id:path}")
async def get_place_details(place_id: str):
    data = await googlemaps_client.get_place_details(place_id)
    return {"data": data}


@app.get("/maps/geocode")
async def geocode_address(address: str = Query(...)):
    data = await googlemaps_client.geocode(address)
    return {"data": data}


@app.get("/maps/reverse-geocode")
async def reverse_geocode(lat: float = Query(...), lng: float = Query(...)):
    data = await googlemaps_client.reverse_geocode(lat, lng)
    return {"data": data}


@app.get("/maps/route")
async def compute_route(
    origin_lat: float = Query(ROBOT_LAT),
    origin_lng: float = Query(ROBOT_LNG),
    dest_lat: float = Query(...),
    dest_lng: float = Query(...),
    travel_mode: str = Query("WALK"),
):
    data = await googlemaps_client.compute_route(origin_lat, origin_lng, dest_lat, dest_lng, travel_mode)
    return {"data": data}


@app.post("/maps/route-matrix")
async def compute_route_matrix(request: RouteMatrixRequest):
    origins = [{"lat": o.lat, "lng": o.lng} for o in request.origins]
    destinations = [{"lat": d.lat, "lng": d.lng} for d in request.destinations]
    data = await googlemaps_client.compute_route_matrix(origins, destinations, request.travel_mode)
    return {"data": data}
