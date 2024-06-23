import os
import sys

{% if "sqlalchemy" in cookiecutter.extra_packages %}
import pytest
import asyncio
import logging
from typing import AsyncIterator

from alembic import command
from alembic.config import Config
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(f"{cwd}/.."))

# the following import only works after sys.path is updated
from main import app, db_session  # noqa

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

{% elif "django" in cookiecutter.extra_packages %}
import pytest

from django.conf import settings
from django.core.management import call_command

{% endif %}

cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(f"{cwd}/.."))

{% if "sqlalchemy" in cookiecutter.extra_packages %}
from {{cookiecutter.pkg_name}}.models import User  # noqa: E402

# helper functions
def is_env_true(var_name: str) -> bool:
    return os.environ.get(var_name, "N").upper() in ["1", "Y", "YES", "TRUE"]


def tmp_sqlite_url():
    tmp_path = os.path.abspath(f"{cwd}/../tmp")
    os.makedirs(tmp_path, exist_ok=True)
    return f"sqlite+aiosqlite:///{tmp_path}/test.db"


def async2sync_database_uri(database_uri: str) -> str:
    """
    translate a async SQLALCHEMY_DATABASE_URI format string
    to a sync format, which can be used by alembic
    """
    if database_uri.startswith("sqlite+aiosqlite:"):
        return database_uri.replace("+aiosqlite", "")
    elif database_uri.startswith("postgresql+asyncpg:"):
        return database_uri.replace("+asyncpg", "+psycopg")
    else:
        return database_uri


def prep_new_test_db(test_db_url: str) -> tuple[bool, str]:
    """
    create a new test database
    run alembic schema migration
    then seed the database with some test data
    return: True if new database created
    """
    db_url = async2sync_database_uri(test_db_url)
    if database_exists(db_url):
        return False, ""

    logger.info(f"creating test database {db_url}")
    create_database(db_url)

    # Run the migrations
    # so we set it so that alembic knows to use the correct database during testing
    os.environ["ALEMBIC_DATABASE_URI"] = db_url
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

    # seed test data
    engine = create_engine(db_url)
    with sessionmaker(autocommit=False, autoflush=False, bind=engine)() as session:
        logger.info("adding seed data")
        seed_data(session)

    return True, db_url


# test database setup for app
# modelled after database.py in the app
test_db_url = os.environ.get("TEST_DATABASE_URI", tmp_sqlite_url())
conn_args = {"check_same_thread": False} if test_db_url.startswith("sqlite") else {}

# sync mode setup, uncomment async version below if needed
testing_sql_engine = create_engine(test_db_url, connect_args=conn_args, echo=False)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=testing_sql_engine)


# Testing Dependency
def testing_db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# uncomment if using async api endpoints
# async_testing_sql_engine = create_async_engine(test_db_url, echo=False)
# AsyncTestingSessionLocal = async_sessionmaker(
#     expire_on_commit=False,
#     class_=AsyncSession,
#     bind=async_testing_sql_engine,
# )


# uncomment if using async api endpoints
# async def testing_db_session() -> AsyncIterator[AsyncSession]:
#     async with AsyncTestingSessionLocal() as session:
#         yield session


# overrides default dependency injection for testing
app.dependency_overrides[db_session] = testing_db_session


# text fixtures
@pytest.fixture(autouse=True, scope="session")
def test_db():
    """
    prepare the test database:
    1. if the database does not exist, create it
    2. run migration on the database
    3. delete the database after the test, unless KEEP_TEST_DB is set to Y
    """
    test_db_created, sync_db_url = prep_new_test_db(test_db_url)

    # the yielded value is not used, but we need this structure to ensure the cleanup code runs
    yield

    # only delete the test database if it was created during this test run
    # to avoid accidental deletion of potentially important data
    if test_db_created and not is_env_true("KEEP_TEST_DB"):
        logger.info(f"dropping test database {sync_db_url}")
        drop_database(sync_db_url)


# uncomment if using async api endpoints
# # in pytest-asyncio the default event loop is function scoped
# # which causes problem with asyncpg
# @pytest.fixture(scope="session")
# def event_loop():
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()

# uncomment if using async api endpoints
# @pytest.fixture()
# async def session():
#     async with AsyncTestingSessionLocal() as session:
#         yield session

@pytest.fixture(scope="session")
def session():
    with TestingSessionLocal() as session:
        yield session

# uncomment if using async api endpoints
# @pytest.fixture(scope="session")
# async def client():
#     async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
#         yield client



def seed_data(session):
    root = User(login_name="root")
    session.add(root)
    session.commit()
{% elif "django" in cookiecutter.extra_packages %}

@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    # in memory db are empty upon start, run schema migrate
    with django_db_blocker.unblock():
        call_command("migrate", interactive=False)
        # load test data if needed
        # seed_data()
{% endif %}
