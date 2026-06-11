import os
from pathlib import Path
from dotenv import load_dotenv
from app.services.supabase_client import SupabaseClient

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

supabase_client = SupabaseClient(service_key=os.getenv("SUPABASE_SERVICE_KEY", ""))

__all__ = ["supabase_client"]
