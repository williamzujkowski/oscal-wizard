from __future__ import annotations

from functools import lru_cache
from typing import Set

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://oscal:oscal@localhost:5432/oscal_wizard"
    secret_key: str = "change-me"
    session_cookie_name: str = "oscal_session"
    session_https_only: bool = False

    github_client_id: str = ""
    github_client_secret: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""

    admin_allowlist: str = ""
    admin_allowlist_enabled: bool = True

    def admin_allowlist_set(self) -> Set[str]:
        if not self.admin_allowlist:
            return set()
        return {email.strip().lower() for email in self.admin_allowlist.split(",") if email.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
