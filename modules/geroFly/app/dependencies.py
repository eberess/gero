import os
from dotenv import load_dotenv
from app.services.airlabs_client import AirlabsClient

load_dotenv()

airlabs_client = AirlabsClient(api_key=os.getenv("AIRLABS_API_KEY", ""))

__all__ = ["airlabs_client"]
