import json
import os
from pathlib import Path
from urllib.parse import urlparse, urlunparse

from openfeature import api
from pydantic_settings import BaseSettings, SettingsConfigDict
from helper import sync2async_database_url

env_file = os.getenv("APP_SETTINGS_ENV", str(Path(__file__).resolve().parent / ".env"))

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # for FastAPI
    app_name: str = "api3"
    api_audience: str = "api3"
    jwks_url: str = ""

{% if "sqlmodel" in cookiecutter.extra_packages %}
    # for SQLModel/SQLAlchemy
    database_url: str = "sqlite:///memory:"
    database_url_async: str = ""
    enable_sqlalchemy_echo: bool = False
    async_orm: bool = False
{% endif %}

    # for OpenFeature
    feature_flags_url: str = "grpc://flagd:8013"
    feature_prefix: str = ""


settings = AppSettings()
settings.feature_prefix = settings.feature_prefix or settings.app_name

{% if "sqlmodel" in cookiecutter.extra_packages %}
if settings.async_orm and not settings.database_url_async:
    # try to derive the async database URL from the sync one
    settings.database_url_async = sync2async_database_url(settings.database_url)
{% endif %}

def _init_feature_client(feature_flags_url: str):
    # the provider should be swappable with any OpenFeature provider
    from openfeature.contrib.provider.flagd import FlagdProvider
    from openfeature.contrib.provider.flagd.config import ResolverType

    parsed = urlparse(feature_flags_url)
    if parsed.scheme == "file":
        provider = FlagdProvider(
            resolver_type=ResolverType.FILE,
            offline_flag_source_path=parsed.path,
        )
    elif parsed.scheme.startswith("grpc"):
        provider = FlagdProvider(
            resolver_type=ResolverType.RPC,
            host=parsed.hostname,
            port=parsed.port,
            tls=parsed.scheme == "grpcs",
        )
    else:
        raise ValueError(f"Unsupported feature flags URL: {feature_flags_url}")

    api.set_provider(provider)
    return api.get_client()


feature_client = _init_feature_client(settings.feature_flags_url)

if __name__ == "__main__":
    print(json.dumps(settings.model_dump(), indent=2))
