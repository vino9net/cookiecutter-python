import logging

logger = logging.getLogger(__name__)

def test_logger():
    logger.info("running test_logger")

{%- if "fastapi" in cookiecutter.extra_packages %}
async def test_healthz(client):
    response = client.get("/healthz")
    assert response.status_code == 200
{%- endif %}

{%- if "tortoise-orm" in cookiecutter.extra_packages %}
async def test_root_user(client):
    response = client.get("/users/root")
    assert response.status_code == 200
{%- endif %}
