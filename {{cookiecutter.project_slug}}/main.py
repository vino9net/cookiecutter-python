from typing import Iterator, AsyncIterator

import uvicorn
from fastapi import FastAPI, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from {{ cookiecutter.pkg_name }} import models

from database import SessionLocal

# Dependency
def db_session() -> Iterator[Session]::
    with SessionLocal() as session:
        yield session

# uncomment below for async version
# async def db_session() -> AsyncIterator[AsyncSession]:
#     async with SessionLocal() as session:
#         yield session

app = FastAPI(docs_url=None, redoc_url=None)

@app.get("/healthz")
def health():
    return "running"


@app.get("/ready")
def ready():
    return "ready"

@app.get("/users/{user_name}")
def read_user(user_name: str, session: Session = Depends(db_session)):
    user = session.execute(select(models.User).filter_by(login_name=user_name)).scalars().first()
    return {"user_id": user.id}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)