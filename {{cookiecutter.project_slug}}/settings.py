import json
import os
from pathlib import Path
from urllib.parse import urlparse, urlunparse

from pydantic_settings import BaseSettings, SettingsConfigDict
from helper import sync2async_database_url

env_file = os.getenv("APP_SETTINGS_ENV", str(Path(__file__).resolve().parent / ".env"))

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "api3"
    api_audience: str = "api3"
    jwks_url: str = ""

{% if "sqlmodel" in cookiecutter.extra_packages %}
    database_url: str = "sqlite:///memory:"
    database_url_async: str = ""
    enable_sqlalchemy_echo: bool = False
    async_orm: bool = False
{% endif %}


settings = AppSettings()  # type: ignore
{% if "sqlmodel" in cookiecutter.extra_packages %}
if settings.async_orm and not settings.database_url_async:
    # try to derive the async database URL from the sync one
    settings.database_url_async = sync2async_database_url(settings.database_url)
{% endif %}

if __name__ == "__main__":
    print(json.dumps(settings.model_dump(), indent=2))
