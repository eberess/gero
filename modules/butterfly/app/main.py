from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.dependencies import supabase_client
from app.llm import router as llm_router

app = FastAPI(
    title="geroButterfly API",
    description="Formation et conformité — Supabase formation/badges/agents",
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
    return {"status": "ok", "service": "geroButterfly"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/formations")
async def list_formations(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    typo: str = Query("", description="Filtrer par typo (T7, T10, T2...)"),
):
    data = await supabase_client.list_formations(limit, offset, typo)
    return data


@app.get("/formations/search")
async def search_formations(nom: str = Query(...), prenom: str = Query("")):
    data = await supabase_client.search_formation(nom, prenom)
    if "error" in data:
        return {"data": data}
    return {"data": data}


@app.get("/formations/{formation_id}")
async def get_formation(formation_id: int):
    data = await supabase_client.get_formation_by_id(formation_id)
    if "error" in data:
        return {"data": data}
    return {"data": data}


@app.get("/profile")
async def agent_profile(nom: str = Query(...), prenom: str = Query("")):
    data = await supabase_client.get_agent_full_profile(nom, prenom)
    if "error" in data:
        return {"data": data}
    return {"data": data}


@app.get("/badges")
async def search_badges(numero: str = Query(""), nom: str = Query("")):
    data = await supabase_client.search_badge(numero, nom)
    return {"data": data}


@app.get("/agents")
async def search_agents(nom: str = Query(...), prenom: str = Query("")):
    data = await supabase_client.search_agent(nom, prenom)
    return {"data": data}


@app.get("/stats/compliance")
async def compliance_stats():
    data = await supabase_client.get_compliance_stats()
    if "error" in data:
        return {"data": data}
    return {"data": data}


@app.get("/stats/expired")
async def expired():
    data = await supabase_client.get_expired()
    if "error" in data:
        return {"data": data}
    return {"data": data}


@app.get("/stats/expiring")
async def expiring(days: int = Query(30, ge=1, le=365)):
    data = await supabase_client.get_expiring_soon(days)
    if "error" in data:
        return {"data": data}
    return {"data": data}


@app.get("/stats/typo")
async def typo_stats():
    data = await supabase_client.get_typo_stats()
    if "error" in data:
        return {"data": data}
    return {"data": data}
