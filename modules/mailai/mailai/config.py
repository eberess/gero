from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class Config:
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

    db_path: str = str(Path.home() / ".mailai" / "mailai.db")

    _loaded: bool = field(default=False, repr=False)

    def load(self, env_file: str | None = None) -> None:
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        self.openai_api_key = os.getenv("OPENAI_API_KEY", self.openai_api_key)
        self.openai_model = os.getenv("OPENAI_MODEL", self.openai_model)

        self.smtp_server = os.getenv("SMTP_SERVER", self.smtp_server)
        smtp_port = os.getenv("SMTP_PORT")
        if smtp_port:
            self.smtp_port = int(smtp_port)
        self.smtp_username = os.getenv("SMTP_USERNAME", self.smtp_username)
        self.smtp_password = os.getenv("SMTP_PASSWORD", self.smtp_password)
        self.smtp_from_email = os.getenv("SMTP_FROM_EMAIL", self.smtp_from_email)
        self.smtp_from_name = os.getenv("SMTP_FROM_NAME", self.smtp_from_name)

        self.imap_server = os.getenv("IMAP_SERVER", self.imap_server)
        imap_port = os.getenv("IMAP_PORT")
        if imap_port:
            self.imap_port = int(imap_port)
        self.imap_username = os.getenv("IMAP_USERNAME", self.imap_username) or self.smtp_username
        self.imap_password = os.getenv("IMAP_PASSWORD", self.imap_password) or self.smtp_password

        db_path = os.getenv("DB_PATH")
        if db_path:
            self.db_path = db_path

        self._loaded = True

    @property
    def is_valid(self) -> tuple[bool, list[str]]:
        errors: list[str] = []
        if not self.openai_api_key:
            errors.append("OPENAI_API_KEY is not set")
        if not self.smtp_username:
            errors.append("SMTP_USERNAME is not set")
        if not self.smtp_password:
            errors.append("SMTP_PASSWORD is not set")
        if not self.smtp_from_email:
            errors.append("SMTP_FROM_EMAIL is not set")
        return (len(errors) == 0, errors)

    @property
    def db_dir(self) -> str:
        return os.path.dirname(self.db_path) or "."


config = Config()
