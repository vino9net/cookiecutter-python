from typing import AsyncIterator, Iterator
import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from settings import settings
from helper import is_in_memory_db

logger = logging.getLogger(__name__)

echo = settings.enable_sqlalchemy_echo

# sync engine is always enabled
db_url = settings.database_url
logger.info(f"creating database async engine with {db_url}")
if is_in_memory_db(db_url):
    # must use StaticPool for in-memory SQLite database
    # in order for different connections to share the same data
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        echo=echo,
        poolclass=StaticPool,
    )
else:
    engine = create_engine(db_url, echo=echo)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def db_session() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


# async engine can be enabled by setting
if settings.async_orm:
    db_url_async = settings.database_url_async
    logger.info(f"creating async database engine with {db_url_async}")
    if is_in_memory_db(db_url_async):
        async_engine = create_async_engine(
            db_url_async,
            connect_args={"check_same_thread": False},
            echo=echo,
            poolclass=StaticPool,
        )
    else:
        async_engine = create_async_engine(db_url_async, echo=echo)

    AsyncSessionLocal = async_sessionmaker(
        bind=async_engine, autoflush=False, future=True
    )


# async_db_session is imported by some modules
# so the defition must be available even when async_orm is False
async def async_db_session() -> AsyncIterator[AsyncSession]:
    if settings.async_orm:
        async with AsyncSessionLocal() as session:
            yield session
