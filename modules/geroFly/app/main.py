from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.dependencies import airlabs_client
from app.llm import router as llm_router

app = FastAPI(
    title="geroFly API",
    description="Flight information microservice for GERO — Airlabs API v9",
    version="1.0.0",
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


@app.get("/")
def read_root():
    return {"status": "ok", "service": "geroFly"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/flights/airport/{iata_code}")
async def get_airport_info(iata_code: str):
    data = await airlabs_client.get_airport(iata_code.upper())
    return {"data": data}


@app.get("/flights/departures/{iata_code}")
async def get_departures(iata_code: str, limit: int = Query(20, ge=1, le=50)):
    data = await airlabs_client.get_departures(iata_code.upper(), limit)
    return {"data": data}


@app.get("/flights/arrivals/{iata_code}")
async def get_arrivals(iata_code: str, limit: int = Query(20, ge=1, le=50)):
    data = await airlabs_client.get_arrivals(iata_code.upper(), limit)
    return {"data": data}


@app.get("/flights/live/{iata_code}")
async def get_live_flights(
    iata_code: str,
    direction: str = Query("departures", pattern="^(departures|arrivals)$"),
):
    data = await airlabs_client.get_live_flights(iata_code.upper(), direction)
    return {"data": data}


@app.get("/flights/status/{flight_iata}")
async def get_flight_status(flight_iata: str):
    data = await airlabs_client.get_flight(flight_iata.upper())
    return {"data": data}


@app.get("/flights/delays/{iata_code}")
async def get_delayed_flights(
    iata_code: str,
    direction: str = Query("departures", pattern="^(departures|arrivals)$"),
    min_delay: int = Query(30, ge=30),
):
    data = await airlabs_client.get_delayed_flights(iata_code.upper(), direction, min_delay)
    return {"data": data}


@app.get("/flights/airline/{iata_code}")
async def get_airline_info(iata_code: str):
    data = await airlabs_client.get_airline(iata_code.upper())
    return {"data": data}
