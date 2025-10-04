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
{% else %}
from http.server import BaseHTTPRequestHandler, HTTPServer
{% endif %}

# Load the logging configuration
LOGGING_CONFIG = {}
with open(Path(__file__).parent / "logger_config.yaml", "r") as f:
    LOGGING_CONFIG = yaml.safe_load(f)
    logging.config.dictConfig(LOGGING_CONFIG)


{% if "fastapi" in cookiecutter.extra_packages %}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # change uvicorn access log format
    logger = logging.getLogger("uvicorn.access")
    console_formatter = uvicorn.logging.ColourizedFormatter(  # pyright: ignore
        LOGGING_CONFIG["formatters"]["standard"]["format"]
    )
    logger.handlers[0].setFormatter(console_formatter)

    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan, redoc_url=None)
app.include_router({{ cookiecutter.pkg_name }}_router)

@app.get("/healthz")
def health():
    return "running"


@app.get("/ready")
def ready():
    return "ready"

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
{% else %}
def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == "__main__":
    run()
{% endif %}
