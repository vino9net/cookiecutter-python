import os
import sys
from loguru import logger

{% if "sqlalchemy" in cookiecutter.extra_packages %}
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

{% endif %}
cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(f"{cwd}/.."))

logger.remove()
logger.add(sys.stdout, level="WARNING", filter="{{ cookiecutter.pkg_name }}")

{% if "sqlalchemy" in cookiecutter.extra_packages %}
from {{ cookiecutter.pkg_name }}.models import User  # noqa: E402


@pytest.fixture(scope="session")
def sql_engine(tmp_path_factory):
    test_db_url = os.environ.get("TEST_DATABASE_URL")
    if test_db_url is None:
        test_db_url = f"sqlite:///{tmp_path_factory.getbasetemp()}/test.db"

    if not database_exists(test_db_url):
        logger.info(f"creating test database {test_db_url}")
        create_database(test_db_url)

    sql_engine = create_engine(test_db_url)

    # Run the migrations
    # set this so that the alembic migration script can find the db url
    os.environ["DATABASE_URL"] = test_db_url
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", test_db_url)
    command.upgrade(alembic_cfg, "head")

    yield sql_engine

    if os.environ.get("KEEP_TEST_DB").upper() not in ["1", "Y", "YES", "TRUE"]:
        # drop the test database
        logger.info(f"dropping test database {test_db_url}")
        drop_database(test_db_url)


@pytest.fixture(scope="session")
def session(sql_engine):
    Session = sessionmaker(bind=sql_engine)
    session = Session()
    seed_data(session)

    yield session

    session.close()


def seed_data(session):
    root = User(login_name="root")
    session.add(root)
    session.commit()
{% endif %}
