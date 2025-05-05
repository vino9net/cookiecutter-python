import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from security import get_jwt_verifier

{% if "tortoise-orm" in cookiecutter.extra_packages %}
from .models import User
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

{% if "tortoise-orm" in cookiecutter.extra_packages %}
@router.get("/users/{user_name}")
async def get_user(user_name: str):
    user = await User.filter(login_name=user_name).first()
    if user:
        return {"user_id": user.id}
{% endif %}
