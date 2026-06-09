import os
from pathlib import Path
from dotenv import load_dotenv
from app.services.airlabs_client import AirlabsClient

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

airlabs_client = AirlabsClient(api_key=os.getenv("AIRLABS_API_KEY", ""))

__all__ = ["airlabs_client"]
