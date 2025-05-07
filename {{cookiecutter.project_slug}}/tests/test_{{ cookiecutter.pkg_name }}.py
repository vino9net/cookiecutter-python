{% if "fastapi" in cookiecutter.extra_packages %}
from unittest.mock import AsyncMock, patch

from settings import settings
from tests.jwt_utils import create_jwt_token


async def test_info(client):
    response = client.get("/api/info")
    assert response.status_code == 200


async def test_secret_unauthenticated(client):
    response = client.get("/api/secret")
    assert response.status_code == 403


@patch("security.get_jwks_data", new_callable=AsyncMock)
async def test_secret_authenticated(mock_get_jwks_data, client, mock_file_content):
    mock_get_jwks_data.return_value = mock_file_content("jwt/jwks.json")
    jwt_token = create_jwt_token(scope="read:data", audience=settings.api_audience)
    response = client.get("/api/secret", headers={"Authorization": "Bearer " + jwt_token})
    assert response.status_code == 200
{% endif %}


{% if "sqlmodel" in cookiecutter.extra_packages %}
async def test_get_user(client, test_db):
    response = client.get("/api/users/root")
    assert response.status_code == 200
{% endif %}

{% if "none" in cookiecutter.extra_packages %}
# this dummy test allow allows pytest to succeed during unit test
# without any tests pytest will return non-zero exit code
def test_dummy():
    assert True
{% endif %}
