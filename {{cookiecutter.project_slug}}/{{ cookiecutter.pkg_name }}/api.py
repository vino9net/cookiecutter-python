import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from security import get_jwt_verifier

{%- if "sqlmodel" in cookiecutter.extra_packages %}
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from {{ cookiecutter.pkg_name }}.models  import User

from database import async_db_session, db_session
{% endif %}

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.get("/info")
async def get_info():
    return {"info": "This is public info"}


@router.get("/secret")
async def get_secret(
    current_user: Annotated[dict, Depends(get_jwt_verifier("read:data"))],
):
    return {"info": "This is secret protected by JWT token"}


{% if "sqlmodel" in cookiecutter.extra_packages %}
@router.get("/users/{user_name}")
def read_user(user_name: str, session: Session = Depends(db_session)):
    user = session.execute(
        select(User).filter_by(login_name=user_name)
    ).scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/async/users/{user_name}")
async def read_user_async(
    user_name: str, session: AsyncSession = Depends(async_db_session)
):
    user = (
        await session.execute(select(User).filter_by(login_name=user_name))
    ).scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
{%- endif %}
