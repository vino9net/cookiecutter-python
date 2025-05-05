from typing import Iterator
from dotenv import load_dotenv
import logging
import logging.config
import yaml
from pathlib import Path

{% if "fastapi" in cookiecutter.extra_packages %}
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from {{ cookiecutter.pkg_name }}.api import router as {{ cookiecutter.pkg_name }}_router
from settings import settings
{% endif %}

{% if "tortoise-orm" in cookiecutter.extra_packages %}
import os
from {{ cookiecutter.pkg_name }}.models import User
{% endif %}

load_dotenv()

logger_config_path = Path(__file__).parent / "logger_config.yaml"
if logger_config_path.exists():
    with open(logger_config_path, "r") as f:
        logging.config.dictConfig(yaml.safe_load(f))

{% if "tortoise-orm" in cookiecutter.extra_packages %}
TORTOISE_ORM = {
    "connections": {"default": os.environ.get("DATABASE_URL")},
    "apps": {
        "models": {
            "models": ["{{ cookiecutter.pkg_name }}.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}
{% endif %}

{% if "fastapi" in cookiecutter.extra_packages %}

@asynccontextmanager
async def lifespan(app: FastAPI):
{% if "tortoise-orm" in cookiecutter.extra_packages %}
    from tortoise.contrib.fastapi import RegisterTortoise

    async with RegisterTortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=False,
    ):
        yield
{% else %}
    yield
{% endif %}


app = FastAPI(lifespan=lifespan, redoc_url=None)
app.include_router({{ cookiecutter.pkg_name }}_router)

@app.get("/healthz")
def health():
    return "running"


@app.get("/ready")
def ready():
    return "ready"
{% endif %}

if __name__ == "__main__":
{% if "fastapi" in cookiecutter.extra_packages %}
    uvicorn.run(app, host="127.0.0.1", port=8000)
{% else %}
    print("main.py")
{% endif %}
