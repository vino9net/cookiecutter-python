from typing import Iterator
from dotenv import load_dotenv

{%- if "fastapi" in cookiecutter.extra_packages %}
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
{%- endif %}

{%- if "tortoise-orm" in cookiecutter.extra_packages %}
import os
from {{ cookiecutter.pkg_name }}.models import User
{%- endif %}

load_dotenv()

{%- if "tortoise-orm" in cookiecutter.extra_packages %}
TORTOISE_ORM = {
    "connections": {"default": os.environ.get("DATABASE_URL")},
    "apps": {
        "models": {
            "models": ["{{ cookiecutter.pkg_name }}.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}
{%- endif %}

{%- if "fastapi" in cookiecutter.extra_packages %}

@asynccontextmanager
async def lifespan(app: FastAPI):
{%- if "tortoise-orm" in cookiecutter.extra_packages %}
    from tortoise.contrib.fastapi import RegisterTortoise

    async with RegisterTortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=False,
    ):
        yield
{%- else %}
    yield
{%- endif %}


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)

@app.get("/healthz")
def health():
    return "running"


@app.get("/ready")
def ready():
    return "ready"
{%- endif %}

{%- if "tortoise-orm" in cookiecutter.extra_packages %}
@app.get("/users/{user_name}")
async def get_user(user_name: str):
    user = await User.filter(login_name=user_name).first()
    if user:
        return {"user_id": user.id}
{%- endif %}


if __name__ == "__main__":
{%- if "fastapi" in cookiecutter.extra_packages %}
    uvicorn.run(app, host="127.0.0.1", port=8000)
{%- else %}
    print("main.py")
{%- endif %}
