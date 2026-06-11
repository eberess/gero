import os
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv


@dataclass
class MailConfig:
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    smtp_server: str = "pro1.mail.ovh.net"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_from_name: str = ""
    imap_server: str = "pro1.mail.ovh.net"
    imap_port: int = 993
    imap_username: str = ""
    imap_password: str = ""
    db_path: str = ""
    _base_dir: str = ""
    _loaded: bool = field(default=False, repr=False)

    def _set_db_path(self, env_val: str) -> None:
        if env_val and env_val.startswith("/app/"):
            self.db_path = str(Path(self._base_dir) / "data" / "mailai.db")
        elif env_val:
            self.db_path = env_val
        else:
            self.db_path = str(Path(self._base_dir) / "data" / "mailai.db")


_config = MailConfig()


def load_config() -> MailConfig:
    global _config
    if _config._loaded:
        return _config

    load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

    _config._base_dir = str(Path(__file__).resolve().parent.parent)
    _config._set_db_path(os.getenv("DB_PATH", ""))

    _config.openai_api_key = os.getenv("OPENAI_API_KEY", "")
    _config.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    _config.smtp_server = os.getenv("SMTP_SERVER", "pro1.mail.ovh.net")
    _config.smtp_username = os.getenv("SMTP_USERNAME", "")
    _config.smtp_password = os.getenv("SMTP_PASSWORD", "")
    _config.smtp_from_email = os.getenv("SMTP_FROM_EMAIL", "")
    _config.smtp_from_name = os.getenv("SMTP_FROM_NAME", "")
    _config.imap_server = os.getenv("IMAP_SERVER", "pro1.mail.ovh.net")
    _config.imap_username = os.getenv("IMAP_USERNAME", "") or _config.smtp_username
    _config.imap_password = os.getenv("IMAP_PASSWORD", "") or _config.smtp_password

    smtp_port = os.getenv("SMTP_PORT")
    if smtp_port:
        _config.smtp_port = int(smtp_port)
    imap_port = os.getenv("IMAP_PORT")
    if imap_port:
        _config.imap_port = int(imap_port)

    _config._loaded = True
    return _config


mail_config = load_config()

__all__ = ["mail_config"]
