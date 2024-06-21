import os
import sys

{% if "sqlalchemy" in cookiecutter.extra_packages %}
import pytest
from alembic import command
from alembic.config import Config
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

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



def tmp_sqlite_url():
    tmp_path = os.path.abspath(f"{cwd}/../tmp")
    os.makedirs(tmp_path, exist_ok=True)
    return f"sqlite:///{tmp_path}/test.db"


test_db_url = os.environ.get("TEST_DATABASE_URI", tmp_sqlite_url())
if test_db_url.startswith("sqlite"):
    db_args = {"check_same_thread": False}
testing_sql_engine = create_engine(test_db_url, connect_args=db_args, echo=False)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=testing_sql_engine)


@pytest.fixture(autouse=True, scope="session")
def test_db():
    """
    prepare the test database:
    1. if the database does not exist, create it
    2. run migration on the database
    3. delete the database after the test, unless KEEP_TEST_DB is set to Y
    """
    test_db_created = False

    if not database_exists(test_db_url):
        logger.info(f"creating test database {test_db_url}")
        create_database(test_db_url)
        test_db_created = True

        # Run the migrations
        # so we set it so that alembic knows to use the correct database during testing
        os.environ["SQLALCHEMY_DATABASE_URI"] = test_db_url
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")

        # seed test data
        with TestingSessionLocal() as session:
            logger.info("adding seed data")
            seed_data(session)

    # the yielded value is not used, but we need this structure to ensure the cleanup code runs
    yield testing_sql_engine

    # only delete the test database if it was created during this test run
    # to avoid accidental deletion of potentially important data
    keep_test_db = os.environ.get("KEEP_TEST_DB", "N").upper() in ["1", "Y", "YES", "TRUE"]
    if test_db_created and not keep_test_db:
        logger.info(f"dropping test database {test_db_url}")
        drop_database(test_db_url)


@pytest.fixture(scope="session")
def session():
    with TestingSessionLocal() as session:
        yield session


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
