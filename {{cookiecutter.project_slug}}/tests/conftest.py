import os
from pathlib import Path
from typing import Callable
import pytest
import logging

{% if "fastapi" in cookiecutter.extra_packages %}
from fastapi.testclient import TestClient
{% endif %}

{% if "sqlmodel" in cookiecutter.extra_packages %}
from sqlalchemy_utils import create_database, database_exists, drop_database
from settings import settings
test_database_url = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")
settings.database_url = test_database_url
{% endif %}
mock_data_path = Path(__file__).parent / "mockdata"

{% if "fastapi" in cookiecutter.extra_packages %}
logging.getLogger("httpx").setLevel(logging.WARNING)
{% endif %}

@pytest.fixture(scope="session")
def mock_file_content() -> Callable:
    def _mock_file_content(file_name):
        with open(mock_data_path / file_name, "r") as f:
            return f.read()

    return _mock_file_content


{% if "fastapi" in cookiecutter.extra_packages %}
@pytest.fixture(scope="session")
def client():
    # keep this import here
    # moving it outside will automitcally import settings
    # and break our mechanism use TEST_DATABASE_URL
    from main import app
    client = TestClient(app)
    yield client
{% endif %}


{% if "sqlmodel" in cookiecutter.extra_packages %}
@pytest.fixture(scope="session")
def test_db():
    """
    prepare the test database:
    1. if the database does not exist, create it
    2. run migration on the database
    3. delete the database after the test, unless KEEP_TEST_DB is set to Y
    """
    # this import statement should stay here
    # we must override settings.database_url first
    # before imporing the database module
    from database import SessionLocal, _is_in_memory_db

    if not _is_in_memory_db(test_database_url):
        print(f"\ncreating test database {test_database_url}")
        test_db_created = _create_test_db(test_database_url)
    else:
        test_db_created = False

    with SessionLocal() as session:
        _seed_data(session)

    # the yielded value is not used, but we need this structure to
    # ensure the cleanup code runs
    yield

    # only delete the test database if it was created during this test run
    # to avoid accidental deletion of potentially important data
    if test_db_created and not _is_env_true("KEEP_TEST_DB"):
        print(f"\ndropping test database {test_database_url}")
        drop_database(test_database_url)


@pytest.fixture(scope="function")
def session(test_db):
    # this import statement should stay here
    # we must override settings.database_url first
    # before imporing the database module
    from database import SessionLocal

    with SessionLocal() as session:
        yield session


def _create_test_db(database_url: str) -> bool:
    """
    create a new test database
    run alembic schema migration
    then seed the database with some test data
    return: True if new database created
    """
    if database_exists(database_url):
        return False
    else:
        create_database(database_url)
        return True


def _seed_data(session):
    from {{ cookiecutter.pkg_name }}.models import Base, User

    Base.metadata.create_all(session.get_bind())
    root = User(login_name="root")
    session.add(root)
    session.commit()


# helper functions
def _is_env_true(var_name: str) -> bool:
    return os.environ.get(var_name, "N").upper() in ["1", "Y", "YES", "TRUE"]
{% endif %}

