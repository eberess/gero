import os
from dotenv import load_dotenv
from app.services.googlemaps_client import GoogleMapsClient

load_dotenv()

ROBOT_LAT = 49.0052
ROBOT_LNG = 2.5770

googlemaps_client = GoogleMapsClient(api_key=os.getenv("GOOGLE_MAPS_API_KEY", ""))

__all__ = ["googlemaps_client", "ROBOT_LAT", "ROBOT_LNG"]
