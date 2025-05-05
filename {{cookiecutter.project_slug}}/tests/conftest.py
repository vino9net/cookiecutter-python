import asyncio
import os
from pathlib import Path
from typing import Callable
import pytest

{% if "fastapi" in cookiecutter.extra_packages %}
from fastapi.testclient import TestClient
{% endif %}

{% if "tortoise-orm" in cookiecutter.extra_packages %}
from {{ cookiecutter.pkg_name }}.models import User
{% endif %}

{% if "fastapi" in cookiecutter.extra_packages %}
from main import app
{% endif %}

mock_data_path = Path(__file__).parent / "mockdata"

{% if "fastapi" in cookiecutter.extra_packages %}
@pytest.fixture(scope="session")
def client():
    client = TestClient(app)
    yield client
{% endif %}

{% if "tortoise-orm" in cookiecutter.extra_packages %}

@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def test_db(request, event_loop):
    import tortoise.contrib.test as tortoise_test
    from tortoise import Tortoise
    from main import TORTOISE_ORM

    test_db_url = os.environ.get("TEST_DATABASE_URL", "sqlite://:memory:")
    TORTOISE_ORM["connections"]["default"] = test_db_url
    event_loop.run_until_complete(tortoise_test._init_db(TORTOISE_ORM))
    event_loop.run_until_complete(seed_db())

    if os.environ.get("KEEP_TEST_DB", "N").upper() not in ["Y", "1"]:
        request.addfinalizer(
            lambda: event_loop.run_until_complete(Tortoise._drop_databases())
        )


async def seed_db():
    await User(login_name="root").save()

{% endif %}

@pytest.fixture(scope="session")
def mock_file_content() -> Callable:
    def _mock_file_content(file_name):
        with open(mock_data_path / file_name, "r") as f:
            return f.read()

    return _mock_file_content

