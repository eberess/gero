import os
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv


@dataclass
class SMSConfig:
    gateway_url: str = "http://sms-gateway:3000"
    gateway_username: str = ""
    gateway_password: str = ""
    sms_scopes: list[str] = field(default_factory=lambda: ["messages:send", "messages:read", "messages:list"])
    token_ttl: int = 3600
    db_path: str = ""
    _loaded: bool = field(default=False, repr=False)


_config = SMSConfig()


def load_config() -> SMSConfig:
    global _config
    if _config._loaded:
        return _config

    load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

    base_dir = str(Path(__file__).resolve().parent.parent)
    env_db = os.getenv("DB_PATH", "")
    _config.db_path = env_db if env_db else f"{base_dir}/data/gerosms.db"

    _config.gateway_url = os.getenv("SMS_GATEWAY_URL", "http://sms-gateway:3000")
    _config.gateway_username = os.getenv("SMS_GATEWAY_USERNAME", "")
    _config.gateway_password = os.getenv("SMS_GATEWAY_PASSWORD", "")

    scopes = os.getenv("SMS_SCOPES", "messages:send,messages:read,messages:list")
    _config.sms_scopes = [s.strip() for s in scopes.split(",") if s.strip()]

    ttl = os.getenv("SMS_TOKEN_TTL")
    if ttl:
        _config.token_ttl = int(ttl)

    _config._loaded = True
    return _config


sms_config = load_config()

__all__ = ["sms_config"]
