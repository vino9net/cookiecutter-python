from typing import Iterator, AsyncIterator

{%- if "fastapi" in cookiecutter.extra_packages %}
import uvicorn
from fastapi import FastAPI, Depends
{%- endif %}

{%- if "sqlmodel" in cookiecutter.extra_packages %}
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from {{ cookiecutter.pkg_name }} import models

from database import SessionLocal

#
# begin of sync db setup, remove and uncomment async setup below if needed
#
def db_session() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session
#
# begin of async db setup, uncomment and remove sync setup above if needed
#
# async def db_session() -> AsyncIterator[AsyncSession]:
#     async with SessionLocal() as session:
#         yield session

{%- endif %}


{%- if "fastapi" in cookiecutter.extra_packages %}

app = FastAPI(docs_url=None, redoc_url=None)

@app.get("/healthz")
def health():
    return "running"


@app.get("/ready")
def ready():
    return "ready"
{%- endif %}

{%- if "sqlmodel" in cookiecutter.extra_packages %}
@app.get("/users/{user_name}")
def read_user(user_name: str, session: Session = Depends(db_session)):
    user = session.execute(select(models.User).filter_by(login_name=user_name)).scalars().first() # noqa: E501
    if user:
        return {"user_id": user.id}
{%- endif %}


if __name__ == "__main__":
{%- if "fastapi" in cookiecutter.extra_packages %}
    uvicorn.run(app, host="127.0.0.1", port=8000)
{%- else %}
    print("main.py")
{%- endif %}
