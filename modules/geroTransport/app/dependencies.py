from app.services.idfm_client import IDFMClient
from app.services.geovelo_client import GeoveloClient
from app.services.velib_client import VelibClient
from app.services.infotrafic_client import InfoTraficClient
from app.services.prochainspassages_client import ProchainsPassagesClient
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("IDFM_API_KEY", "")

idfm_client = IDFMClient(api_key=api_key)
geovelo_client = GeoveloClient(api_key=api_key)
velib_client = VelibClient(api_key=api_key)
infotrafic_client = InfoTraficClient(api_key=api_key)
prochainspassages_client = ProchainsPassagesClient(api_key=api_key)

__all__ = [
    "idfm_client", "geovelo_client", "velib_client",
    "infotrafic_client", "prochainspassages_client",
]
