import json
import logging
from typing import Callable, List

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from settings import settings

logger = logging.getLogger(__name__)

security = HTTPBearer()

_signer_jwks = None


async def get_jwks_data() -> dict:
    global _signer_jwks
    if _signer_jwks:
        return _signer_jwks

    url = settings.jwks_url
    if url.startswith("https://"):
        logger.info(f"Fetching public key from {url}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                _signer_jwks = response.json()
                return _signer_jwks
        except httpx.HTTPStatusError as e:
            logger.info(f"HTTPStatusError: {e} when fetching from {url}")
    elif url[0] == "{" and url[-1] == "}":
        # treat it as a json string
        try:
            _signer_jwks = json.loads(url)
            return _signer_jwks
        except json.JSONDecodeError:
            logger.info(f"Invalid JSON string {url}")

    raise RuntimeError(f"Unable to get jwks from {url}")


def get_jwt_verifier(required_scope: str) -> Callable:
    async def verify_jwt_token(
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> dict:
        signer_jwks = await get_jwks_data()
        token = credentials.credentials
        try:
            payload = jwt.decode(token, signer_jwks, audience=settings.api_audience)
            scopes: List[str] = payload.get("scope", "").split()
            if required_scope not in scopes:
                logger.info(
                    f"Token contains scopes: {scopes} does not have required scope: {required_scope}"  # noqa: E501
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required scope: {required_scope}",
                )
            return payload
        except JWTError as e:
            logger.info(f"JWTError: Invalid token {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

    return verify_jwt_token
