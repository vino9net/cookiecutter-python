import json
import os
from pathlib import Path
from urllib.parse import urlparse, urlunparse

from pydantic_settings import BaseSettings, SettingsConfigDict


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

def _sync2async_database_url(database_url: str) -> str:
    """
    translate a database_url with a sync driver
    to one with async ddriver
    """
    parsed = urlparse(database_url)
    parts = parsed.scheme.split("+")
    db_type, driver = parts[0], parts[1] if len(parts) > 1 else ""
    if db_type == "postgresql" and driver == "psycopg":
        driver = "psycopg_async"
    elif db_type == "mysql" and driver == "mysqldb":
        driver = "aiomysql"
    elif db_type == "sqlite" and driver == "":
        driver = "aiosqlite"
    else:
        # for unsupported database types, we just return the original URL
        raise RuntimeError("Unsupported database type {database_url}")

    return urlunparse(parsed._replace(scheme=f"{db_type}+{driver}"))
{% endif %}


settings = AppSettings()  # type: ignore
{% if "sqlmodel" in cookiecutter.extra_packages %}
if settings.async_orm and settings.database_url_async is None:
    # try to derive the async database URL from the sync one
    settings.database_url_async = _sync2async_database_url(settings.database_url)
{% endif %}

if __name__ == "__main__":
    print(json.dumps(settings.model_dump(), indent=2))
