from fastapi import FastAPI, HTTPException, Query
from app.services.idfm_client import IDFMClient
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="geroTransport API",
    description="Module d'intelligence de transport pour Unitree G1 utilisant Navitia V2",
    version="1.0.0"
)

idfm_client = IDFMClient(api_key=os.getenv("IDFM_API_KEY", ""))

@app.get("/")
def read_root():
    return {"status": "ok", "service": "geroTransport"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/transport/search")
async def search_place(q: str = Query(..., description="Nom de l'arrêt ou lieu (ex: Aeroport Charles de Gaulle)")):
    """
    Recherche un arrêt ou un lieu pour obtenir son ID Navitia.
    """
    data = await idfm_client.search_place(q)
    return {"data": data}

@app.get("/transport/cdg/departures")
async def get_cdg_departures(stop_id: str = Query("stop_area:IDFM:71876", description="ID de l'arrêt (Défaut: Aéroport CDG 1/2/3)")):
    """
    Récupère les prochains départs (RER, Bus, etc.) à un arrêt spécifique de l'aéroport.
    Par défaut, interroge la zone de l'Aéroport CDG.
    """
    data = await idfm_client.get_departures(stop_id)
    return {"data": data}

@app.get("/transport/journey")
async def get_journey(
    from_point: str = Query(..., description="Point de départ (ID Navitia ou coordonnées lon;lat)"),
    to_point: str = Query(..., description="Point d'arrivée (ID Navitia ou coordonnées lon;lat)")
):
    """
    Calcule l'itinéraire optimal entre deux points.
    Exemple Paris Châtelet vers CDG : from_point=stop_area:IDFM:71410 & to_point=stop_area:IDFM:71876
    """
    data = await idfm_client.get_journey(from_point, to_point)
    return {"data": data}
