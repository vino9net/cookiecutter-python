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

# Load the logging configuration
LOGGING_CONFIG = {}
with open(Path(__file__).parent / "logger_config.yaml", "r") as f:
    LOGGING_CONFIG = yaml.safe_load(f)
    logging.config.dictConfig(LOGGING_CONFIG)

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
    # change uvicorn access log format
    logger = logging.getLogger("uvicorn.access")
    console_formatter = uvicorn.logging.ColourizedFormatter(LOGGING_CONFIG["formatters"]["standard"]["format"]) # pyright: ignore
    logger.handlers[0].setFormatter(console_formatter)
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
