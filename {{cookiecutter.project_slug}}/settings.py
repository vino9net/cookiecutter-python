from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "{{ cookiecutter.pkg_name }}"
    api_audience: str = "{{ cookiecutter.pkg_name }}"
    jwks_url: str
{% if "sqlmodel" in cookiecutter.extra_packages %}
    sqlalchemy_database_uri: str = "sqlite:///memory:"
    async_orm: bool = False
{% endif %}


settings = AppSettings()  # type: ignore

if __name__ == "__main__":
    print(settings.dict())
